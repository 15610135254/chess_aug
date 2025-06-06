class ChessRules:
    @staticmethod
    def check_game_over(board):
        """
        检查游戏是否结束
        返回: {'game_over': bool, 'winner': str or None}
        """
        # 检查红方的帅是否还在棋盘上
        red_king_exists = False
        # 检查黑方的将是否还在棋盘上
        black_general_exists = False

        for piece in board.pieces:
            # 只检查未被吃掉的棋子（坐标不是99,99）
            if piece['x'] != 99 and piece['y'] != 99:
                if piece['name'] == '帅' and piece['type'] == 'red':
                    red_king_exists = True
                elif piece['name'] == '将' and piece['type'] == 'black':
                    black_general_exists = True

        # 判断胜利条件
        if not red_king_exists:
            return {'game_over': True, 'winner': 'black'}
        elif not black_general_exists:
            return {'game_over': True, 'winner': 'red'}
        else:
            return {'game_over': False, 'winner': None}

    @staticmethod
    def is_valid_move(board, from_x, from_y, to_x, to_y):
        result = ChessRules.validate_move_with_reason(board, from_x, from_y, to_x, to_y)
        return result['valid']

    @staticmethod
    def validate_move_with_reason(board, from_x, from_y, to_x, to_y):
        """
        验证移动并返回详细原因
        返回: {'valid': bool, 'reason': str}
        """
        piece = board.get_piece_at(from_x, from_y)
        if not piece:
            return {'valid': False, 'reason': '起始位置没有棋子'}

        # 检查目标位置是否在棋盘内
        if not (0 <= to_x < 9 and 0 <= to_y < 10):
            return {'valid': False, 'reason': '目标位置超出棋盘范围'}

        # 检查是否移动到相同位置
        if from_x == to_x and from_y == to_y:
            return {'valid': False, 'reason': '不能移动到相同位置'}

        # 检查目标位置是否有己方棋子
        target_piece = board.get_piece_at(to_x, to_y)
        if target_piece and target_piece['type'] == piece['type']:
            return {'valid': False, 'reason': '不能吃掉己方棋子'}

        # 根据棋子类型验证移动规则
        piece_name = piece['name']

        if piece_name in ['车']:
            valid = ChessRules._validate_rook_move(board, from_x, from_y, to_x, to_y)
        elif piece_name in ['马']:
            valid = ChessRules._validate_horse_move(board, from_x, from_y, to_x, to_y)
        elif piece_name in ['相', '象']:
            valid = ChessRules._validate_elephant_move(board, from_x, from_y, to_x, to_y, piece['type'])
        elif piece_name in ['仕', '士']:
            valid = ChessRules._validate_advisor_move(board, from_x, from_y, to_x, to_y, piece['type'])
        elif piece_name in ['帅', '将']:
            valid = ChessRules._validate_king_move(board, from_x, from_y, to_x, to_y, piece['type'])
        elif piece_name in ['兵', '卒']:
            valid = ChessRules._validate_pawn_move(board, from_x, from_y, to_x, to_y, piece['type'])
        elif piece_name in ['炮']:
            valid = ChessRules._validate_cannon_move(board, from_x, from_y, to_x, to_y)
        else:
            valid = False

        if not valid:
            return {'valid': False, 'reason': f'{piece_name}的移动规则不允许此移动'}

        # 如果基本移动规则验证通过，再检查帅将相对规则
        if not ChessRules._check_kings_facing(board, from_x, from_y, to_x, to_y):
            return {'valid': False, 'reason': '帅将不能在同一列上直接相对'}

        return {'valid': True, 'reason': '移动合法'}
    
    @staticmethod
    def _validate_rook_move(board, from_x, from_y, to_x, to_y):
        # 车：直线移动，不能越子
        if from_x != to_x and from_y != to_y:
            return False
        
        # 检查路径上是否有棋子
        if from_x == to_x:  # 垂直移动
            start_y, end_y = min(from_y, to_y), max(from_y, to_y)
            for y in range(start_y + 1, end_y):
                if board.get_piece_at(from_x, y):
                    return False
        else:  # 水平移动
            start_x, end_x = min(from_x, to_x), max(from_x, to_x)
            for x in range(start_x + 1, end_x):
                if board.get_piece_at(x, from_y):
                    return False
        
        return True
    
    @staticmethod
    def _validate_horse_move(board, from_x, from_y, to_x, to_y):
        # 马：日字形移动，不能蹩马腿
        dx = abs(to_x - from_x)
        dy = abs(to_y - from_y)
        
        if not ((dx == 2 and dy == 1) or (dx == 1 and dy == 2)):
            return False
        
        # 检查蹩马腿
        if dx == 2:
            # 水平方向移动2格
            block_x = from_x + (1 if to_x > from_x else -1)
            if board.get_piece_at(block_x, from_y):
                return False
        else:
            # 垂直方向移动2格
            block_y = from_y + (1 if to_y > from_y else -1)
            if board.get_piece_at(from_x, block_y):
                return False
        
        return True
    
    @staticmethod
    def _validate_elephant_move(board, from_x, from_y, to_x, to_y, piece_type):
        # 象/相：田字格移动，不能过河，不能越子
        dx = abs(to_x - from_x)
        dy = abs(to_y - from_y)
        
        if dx != 2 or dy != 2:
            return False
        
        # 检查是否过河
        if piece_type == 'red' and to_y < 5:
            return False
        if piece_type == 'black' and to_y > 4:
            return False
        
        # 检查田字中心是否有棋子
        center_x = from_x + (1 if to_x > from_x else -1)
        center_y = from_y + (1 if to_y > from_y else -1)
        if board.get_piece_at(center_x, center_y):
            return False
        
        return True
    
    @staticmethod
    def _validate_advisor_move(board, from_x, from_y, to_x, to_y, piece_type):
        # 士/仕：斜线移动，限制在九宫格内
        dx = abs(to_x - from_x)
        dy = abs(to_y - from_y)
        
        if dx != 1 or dy != 1:
            return False
        
        # 检查是否在九宫格内
        if piece_type == 'red':
            if not (3 <= to_x <= 5 and 7 <= to_y <= 9):
                return False
        else:
            if not (3 <= to_x <= 5 and 0 <= to_y <= 2):
                return False
        
        return True
    
    @staticmethod
    def _validate_king_move(board, from_x, from_y, to_x, to_y, piece_type):
        # 将/帅：上下左右移动，限制在九宫格内
        dx = abs(to_x - from_x)
        dy = abs(to_y - from_y)
        
        if not ((dx == 1 and dy == 0) or (dx == 0 and dy == 1)):
            return False
        
        # 检查是否在九宫格内
        if piece_type == 'red':
            if not (3 <= to_x <= 5 and 7 <= to_y <= 9):
                return False
        else:
            if not (3 <= to_x <= 5 and 0 <= to_y <= 2):
                return False
        
        return True
    
    @staticmethod
    def _validate_pawn_move(board, from_x, from_y, to_x, to_y, piece_type):
        # 兵/卒：未过河只能前进，过河后可左右移动
        dx = abs(to_x - from_x)
        dy = abs(to_y - from_y)
        
        if not ((dx == 1 and dy == 0) or (dx == 0 and dy == 1)):
            return False
        
        if piece_type == 'red':
            # 红兵
            if from_y > 4:  # 未过河
                if dx != 0 or to_y != from_y - 1:
                    return False
            else:  # 已过河
                if dy != 0 and to_y != from_y - 1:
                    return False
        else:
            # 黑卒
            if from_y < 5:  # 未过河
                if dx != 0 or to_y != from_y + 1:
                    return False
            else:  # 已过河
                if dy != 0 and to_y != from_y + 1:
                    return False
        
        return True
    
    @staticmethod
    def _validate_cannon_move(board, from_x, from_y, to_x, to_y):
        # 炮：直线移动，吃子需要隔一个棋子
        if from_x != to_x and from_y != to_y:
            return False
        
        target_piece = board.get_piece_at(to_x, to_y)
        
        # 计算路径上的棋子数量
        piece_count = 0
        if from_x == to_x:  # 垂直移动
            start_y, end_y = min(from_y, to_y), max(from_y, to_y)
            for y in range(start_y + 1, end_y):
                if board.get_piece_at(from_x, y):
                    piece_count += 1
        else:  # 水平移动
            start_x, end_x = min(from_x, to_x), max(from_x, to_x)
            for x in range(start_x + 1, end_x):
                if board.get_piece_at(x, from_y):
                    piece_count += 1
        
        if target_piece:
            # 吃子：需要隔一个棋子
            return piece_count == 1
        else:
            # 移动：路径上不能有棋子
            return piece_count == 0

    @staticmethod
    def _check_kings_facing(board, from_x, from_y, to_x, to_y):
        """
        检查帅将相对规则：帅和将不能在同一列上直接相对（中间没有其他棋子阻挡）
        """
        # 创建临时棋盘状态来模拟移动后的情况
        temp_board = [[None for _ in range(9)] for _ in range(10)]

        # 复制当前棋盘状态
        for y in range(10):
            for x in range(9):
                temp_board[y][x] = board.board[y][x]

        # 执行移动
        moving_piece = temp_board[from_y][from_x]
        temp_board[from_y][from_x] = None
        temp_board[to_y][to_x] = moving_piece

        # 找到红方帅和黑方将的位置
        red_king_pos = None
        black_general_pos = None

        for y in range(10):
            for x in range(9):
                piece = temp_board[y][x]
                if piece:
                    if piece['name'] == '帅' and piece['type'] == 'red':
                        red_king_pos = (x, y)
                    elif piece['name'] == '将' and piece['type'] == 'black':
                        black_general_pos = (x, y)

        # 如果找不到帅或将，说明已经被吃掉，不需要检查相对规则
        if not red_king_pos or not black_general_pos:
            return True

        # 检查是否在同一列
        if red_king_pos[0] == black_general_pos[0]:
            # 在同一列，检查中间是否有棋子阻挡
            col = red_king_pos[0]
            start_y = min(red_king_pos[1], black_general_pos[1])
            end_y = max(red_king_pos[1], black_general_pos[1])

            # 检查中间是否有棋子
            for y in range(start_y + 1, end_y):
                if temp_board[y][col] is not None:
                    return True  # 有棋子阻挡，允许移动

            # 没有棋子阻挡，帅将相对，不允许移动
            return False

        # 不在同一列，允许移动
        return True
