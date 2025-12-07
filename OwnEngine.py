try:
    from treys import Card, Evaluator, Deck
    TREYS_AVAILABLE = True
except ImportError:
    print("ERROR: treys library not installed!")
    print("Install with: pip install treys")
    TREYS_AVAILABLE = False

import random

def normalize_card(card):
    """
    Convert card to treys format:
    - Your game: 'KD', '10H', 'AS'
    - treys wants: 'Kd', 'Th', 'As'
    """
    if len(card) < 2:
        return card
    
    rank = card[:-1]
    if rank == '10':
        rank = 'T'
    suit = card[-1].lower()
    
    return rank + suit

def analyze_game_state(game_state):
    """
    Analyze poker game state and return action with bet size
    
    Returns:
        tuple: (action, bet_percentage)
        - action: "FOLD", "CHECK", "CALL", "RAISE"
        - bet_percentage: 0.0 to 1.0 (percentage of total money)
    """
    if not TREYS_AVAILABLE:
        return ("CHECK", 0.0)
    
    hole_cards = game_state.get('hole_cards', [])
    community_cards = game_state.get('community_cards', [])
    
    # print(f"\nAnalyzing: Hole={hole_cards}, Board={community_cards}")
    
    try:
        hole_normalized = [normalize_card(card) for card in hole_cards]
        board_normalized = [normalize_card(card) for card in community_cards]
        
        hole = [Card.new(card) for card in hole_normalized]
        board = [Card.new(card) for card in board_normalized]
        
        print(f"Normalized: Hole={hole_normalized}, Board={board_normalized}")
    except Exception as e:
        print(f"Error converting cards: {e}")
        return ("CHECK", 0.0)
    
    evaluator = Evaluator()
    
    # PRE-FLOP (no community cards)
    if len(community_cards) == 0:
        return preflop_strategy(hole_cards)
    
    # POST-FLOP (3+ community cards)
    elif len(community_cards) >= 3:
        hand_rank = evaluator.evaluate(board, hole)
        hand_class = evaluator.get_rank_class(hand_rank)
        hand_class_name = evaluator.class_to_string(hand_class)
        
        print(f"Hand rank: {hand_rank}/7462")
        print(f"Hand class: {hand_class_name}")
        
        # Calculate pot odds and equity if not all cards shown
        if len(community_cards) < 5:
            equity = calculate_equity(hole, board)
            print(f"Estimated equity: {equity:.2%}")
            
            if equity > 0.70:
                bet_size = min(0.8, equity)  # Big raise
                return ("RAISE", bet_size)
            elif equity > 0.60:
                bet_size = min(0.5, equity * 0.8)  # Medium raise
                return ("RAISE", bet_size)
            elif equity > 0.40:
                return ("CALL", 0.0)
            else:
                return ("FOLD", 0.0)
        
        # River (all 5 community cards)
        else:
            print(f"River decision - hand_class={hand_class}")
            
            if hand_class <= 2:  # Straight Flush, Four of a Kind
                print("  -> Monster hand!")
                # All-in or near all-in
                bet_size = 0.8 + (hand_rank <= 10) * 0.2  # 0.8-1.0
                return ("RAISE", bet_size)
            
            elif hand_class <= 4:  # Full House, Flush
                print("  -> Strong hand!")
                # Big bet (50-75% of stack)
                bet_size = 0.5 + (2000 - min(hand_rank, 2000)) / 2000 * 0.25
                return ("RAISE", bet_size)
            
            elif hand_class == 5:  # Straight
                print("  -> Good hand!")
                # Medium bet (30-50% of stack)
                bet_size = 0.3 + (3000 - min(hand_rank, 3000)) / 3000 * 0.2
                return ("RAISE", bet_size)
            
            elif hand_rank <= 2000:  # Strong trips or two pair
                print("  -> Decent hand!")
                # Small-medium bet (20-40% of stack)
                bet_size = 0.2 + (2000 - hand_rank) / 2000 * 0.2
                return ("RAISE", bet_size)
            
            elif hand_rank <= 4000:  # Decent hands
                print("  -> Marginal hand!")
                return ("CALL", 0.0)
            
            else:  # Weak hands
                print("  -> Weak hand!")
                return ("FOLD", 0.0)
    
    return ("CHECK", 0.0)


def preflop_strategy(hole_cards):
    """
    Simple preflop strategy with bet sizing
    
    Returns:
        tuple: (action, bet_percentage)
    """
    if len(hole_cards) != 2:
        return ("CHECK", 0.0)
    
    card1, card2 = hole_cards[0], hole_cards[1]
    
    # Handle rank (support both '10' and single character ranks)
    if len(card1) == 3:
        rank1 = card1[:2]
        suit1 = card1[2]
    else:
        rank1 = card1[0]
        suit1 = card1[1]
    
    if len(card2) == 3:
        rank2 = card2[:2]
        suit2 = card2[2]
    else:
        rank2 = card2[0]
        suit2 = card2[1]
    
    rank_values = {'A': 14, 'K': 13, 'Q': 12, 'J': 11, 'T': 10, '10': 10}
    for i in range(2, 10):
        rank_values[str(i)] = i
    
    val1 = rank_values.get(rank1, 0)
    val2 = rank_values.get(rank2, 0)
    
    is_pair = (rank1 == rank2)
    is_suited = (suit1 == suit2)
    high_card = max(val1, val2)
    low_card = min(val1, val2)
    
    print(f"Preflop: pair={is_pair}, suited={is_suited}, high={high_card}, low={low_card}")
    
    # Premium hands - Big raise (50-80% of stack)
    if is_pair and high_card >= 13:  # AA, KK
        print("  -> Premium pocket pair!")
        return ("RAISE", 0.75)
    
    if is_pair and high_card >= 10:  # QQ, JJ, TT
        print("  -> Premium pair!")
        return ("RAISE", 0.5)
    
    if high_card == 14 and low_card >= 13:  # AK
        print("  -> Premium high cards!")
        return ("RAISE", 0.5)
    
    if high_card >= 13 and low_card >= 12:  # AQ, KQ
        print("  -> Premium high cards!")
        return ("RAISE", 0.3)
    
    # Good hands - Small raise (20-40% of stack)
    if is_pair and high_card >= 7:  # 77-99
        print("  -> Good pair!")
        return ("RAISE", 0.25)
    
    if high_card == 14 and low_card >= 10:  # AJ, AT
        print("  -> Ace-high!")
        return ("RAISE", 0.2)
    
    if is_suited and high_card >= 12 and low_card >= 10:  # Suited broadway
        print("  -> Suited connectors!")
        return ("RAISE", 0.15)
    
    return("CALL",0)
    # # Marginal hands - Call or check
    # if is_pair and high_card >= 5:  # 55, 66
    #     print("  -> Small pair!")
    #     return ("CALL", 0.0)
    
    # if high_card >= 11:  # Face card
    #     print("  -> Face card!")
    #     return ("CALL", 0.0)
    
    # # Weak hands - Fold
    # print("  -> Weak hand!")
    # return ("FOLD", 0.0)


def calculate_equity(hole, board):
    """Calculate equity via Monte Carlo"""
    evaluator = Evaluator()
    deck = Deck()
    
    for card in hole + board:
        deck.cards.remove(card)
    
    wins = 0
    ties = 0
    simulations = 500
    cards_needed = 5 - len(board)
    
    for _ in range(simulations):
        remaining = deck.cards.copy()
        random.shuffle(remaining)
        simulated_board = board + remaining[:cards_needed]
        
        our_rank = evaluator.evaluate(simulated_board, hole)
        opponent_hole = remaining[cards_needed:cards_needed+2]
        opponent_rank = evaluator.evaluate(simulated_board, opponent_hole)
        
        if our_rank < opponent_rank:
            wins += 1
        elif our_rank == opponent_rank:
            ties += 1
    
    equity = (wins + ties * 0.5) / simulations
    return equity


if __name__ == "__main__":
    print("="*60)
    print("POKER HAND ANALYZER WITH BET SIZING")
    print("="*60)
    
    test_cases = [
        # Pre-flop
        {
            'name': 'Pocket Aces',
            'state': {'hole_cards': ['AS', 'AH'], 'community_cards': [], 'timestamp': '00:00:00'},
        },
        {
            'name': 'Pocket Kings',
            'state': {'hole_cards': ['KD', 'KC'], 'community_cards': [], 'timestamp': '00:00:00'},
        },
        {
            'name': 'AK offsuit',
            'state': {'hole_cards': ['AS', 'KD'], 'community_cards': [], 'timestamp': '00:00:00'},
        },
        {
            'name': 'Pocket Eights',
            'state': {'hole_cards': ['8D', '8C'], 'community_cards': [], 'timestamp': '00:00:00'},
        },
        {
            'name': '7-2 offsuit',
            'state': {'hole_cards': ['7H', '2C'], 'community_cards': [], 'timestamp': '00:00:00'},
        },
        
        # River hands
        {
            'name': 'Royal Flush',
            'state': {'hole_cards': ['KD', 'QD'], 'community_cards': ['AD', 'JD', '10D', '9H', '5S'], 'timestamp': '00:03:00'},
        },
        {
            'name': 'Four of a Kind',
            'state': {'hole_cards': ['KD', 'KC'], 'community_cards': ['KS', 'KH', '10D', '9H', '5S'], 'timestamp': '00:03:00'},
        },
        {
            'name': 'Full House',
            'state': {'hole_cards': ['KD', 'KC'], 'community_cards': ['KS', '10H', '10D', '9H', '5S'], 'timestamp': '00:03:00'},
        },
        {
            'name': 'Flush',
            'state': {'hole_cards': ['KH', '8H'], 'community_cards': ['4H', 'JH', '9H', '7S', '5S'], 'timestamp': '00:03:00'},
        },
        {
            'name': 'Straight',
            'state': {'hole_cards': ['8D', '9C'], 'community_cards': ['6H', '7S', '10D', 'KC', '2H'], 'timestamp': '00:03:00'},
        },
        {
            'name': 'Three of a Kind',
            'state': {'hole_cards': ['KD', '9C'], 'community_cards': ['KS', 'KH', '7D', '3H', '2S'], 'timestamp': '00:03:00'},
        },
        {
            'name': 'Two Pair',
            'state': {'hole_cards': ['KD', '10C'], 'community_cards': ['KS', '10H', '7D', '3H', '2S'], 'timestamp': '00:03:00'},
        },
        {
            'name': 'One Pair (Aces)',
            'state': {'hole_cards': ['AD', 'KC'], 'community_cards': ['AS', '10H', '7D', '3H', '2S'], 'timestamp': '00:03:00'},
        },
        {
            'name': 'High Card (nothing)',
            'state': {'hole_cards': ['KD', 'JC'], 'community_cards': ['9S', '7H', '5D', '3H', '2S'], 'timestamp': '00:03:00'},
        },
    ]
    
    for i, test in enumerate(test_cases):
        print(f"\n{'='*60}")
        print(f"TEST {i+1}: {test['name']}")
        print('-'*60)
        
        action, bet_size = analyze_game_state(test['state'])
        
        print(f"\n>>> Action: {action}")
        if bet_size > 0:
            print(f">>> Bet Size: {bet_size:.1%} of stack (${bet_size * 1000:.0f} if stack is $1000)")
        print()