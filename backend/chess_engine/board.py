class ChessBoard:
    def __init__(self, board_string=None):
        self.board = [[None for _ in range(9)] for _ in range(10)]
        self.pieces = []
        
        if board_string:
            self.load_from_string(board_string)
        else:
            self.init_default_board()
    
    def init_default_board(self):
        # 初始化默认棋盘布局，与spark_chess_analysis.py的create_initial_board()完全一致
        # 使用9列×10行坐标系统（00-89），180字符格式

        # 黑方棋子 (上方)
        black_pieces = [
            # 第0行：车马象士将士象马车（坐标00,10,20,30,40,50,60,70,80）
            {'name': '车', 'x': 0, 'y': 0, 'type': 'black'},
            {'name': '马', 'x': 1, 'y': 0, 'type': 'black'},
            {'name': '象', 'x': 2, 'y': 0, 'type': 'black'},
            {'name': '士', 'x': 3, 'y': 0, 'type': 'black'},
            {'name': '将', 'x': 4, 'y': 0, 'type': 'black'},
            {'name': '士', 'x': 5, 'y': 0, 'type': 'black'},
            {'name': '象', 'x': 6, 'y': 0, 'type': 'black'},
            {'name': '马', 'x': 7, 'y': 0, 'type': 'black'},
            {'name': '车', 'x': 8, 'y': 0, 'type': 'black'},
            # 第2行：炮（坐标12和72）
            {'name': '炮', 'x': 1, 'y': 2, 'type': 'black'},
            {'name': '炮', 'x': 7, 'y': 2, 'type': 'black'},
            # 第3行：兵（坐标03,23,43,63,83）
            {'name': '卒', 'x': 0, 'y': 3, 'type': 'black'},
            {'name': '卒', 'x': 2, 'y': 3, 'type': 'black'},
            {'name': '卒', 'x': 4, 'y': 3, 'type': 'black'},
            {'name': '卒', 'x': 6, 'y': 3, 'type': 'black'},
            {'name': '卒', 'x': 8, 'y': 3, 'type': 'black'}
        ]

        # 红方棋子 (下方)
        red_pieces = [
            # 第6行：兵（坐标06,26,46,66,86）
            {'name': '兵', 'x': 0, 'y': 6, 'type': 'red'},
            {'name': '兵', 'x': 2, 'y': 6, 'type': 'red'},
            {'name': '兵', 'x': 4, 'y': 6, 'type': 'red'},
            {'name': '兵', 'x': 6, 'y': 6, 'type': 'red'},
            {'name': '兵', 'x': 8, 'y': 6, 'type': 'red'},
            # 第7行：炮（坐标17和77）
            {'name': '炮', 'x': 1, 'y': 7, 'type': 'red'},
            {'name': '炮', 'x': 7, 'y': 7, 'type': 'red'},
            # 第9行：车马象士将士象马车（坐标09,19,29,39,49,59,69,79,89）
            {'name': '车', 'x': 0, 'y': 9, 'type': 'red'},
            {'name': '马', 'x': 1, 'y': 9, 'type': 'red'},
            {'name': '相', 'x': 2, 'y': 9, 'type': 'red'},
            {'name': '仕', 'x': 3, 'y': 9, 'type': 'red'},
            {'name': '帅', 'x': 4, 'y': 9, 'type': 'red'},
            {'name': '仕', 'x': 5, 'y': 9, 'type': 'red'},
            {'name': '相', 'x': 6, 'y': 9, 'type': 'red'},
            {'name': '马', 'x': 7, 'y': 9, 'type': 'red'},
            {'name': '车', 'x': 8, 'y': 9, 'type': 'red'}
        ]

        self.pieces = black_pieces + red_pieces
        self.update_board()
    
    def update_board(self):
        # 清空棋盘
        self.board = [[None for _ in range(9)] for _ in range(10)]

        # 放置棋子
        for piece in self.pieces:
            x, y = piece['x'], piece['y']
            # 检查坐标是否有效（99表示被吃掉的棋子）
            if x != 99 and y != 99:
                # 添加边界检查防止索引越界
                if 0 <= x < 9 and 0 <= y < 10:
                    self.board[y][x] = piece
                else:
                    # 记录无效坐标的警告，但不中断程序
                    print(f"警告: 棋子 {piece['name']} 坐标超出边界: ({x}, {y})")
                    # 将无效坐标的棋子标记为被吃掉
                    piece['x'] = 99
                    piece['y'] = 99
    
    def get_piece_at(self, x, y):
        if 0 <= x < 9 and 0 <= y < 10:
            return self.board[y][x]
        return None
    
    def move_piece(self, from_x, from_y, to_x, to_y):
        # 验证起始和目标坐标是否在有效范围内
        if not (0 <= from_x < 9 and 0 <= from_y < 10):
            return {'success': False, 'game_over': False, 'winner': None}
        if not (0 <= to_x < 9 and 0 <= to_y < 10):
            return {'success': False, 'game_over': False, 'winner': None}

        piece = self.get_piece_at(from_x, from_y)
        if not piece:
            return {'success': False, 'game_over': False, 'winner': None}

        # 检查目标位置是否有棋子
        target_piece = self.get_piece_at(to_x, to_y)
        if target_piece:
            # 吃子：将被吃棋子移出棋盘
            target_piece['x'] = 99
            target_piece['y'] = 99

        # 移动棋子
        piece['x'] = to_x
        piece['y'] = to_y

        self.update_board()

        # 检查游戏是否结束
        from .rules import ChessRules
        game_status = ChessRules.check_game_over(self)

        return {
            'success': True,
            'game_over': game_status['game_over'],
            'winner': game_status['winner']
        }
    
    def to_string(self):
        # 将棋盘状态转换为180字符的字符串格式（与spark_chess_analysis.py兼容）
        # 9列x10行 = 90个位置，每个位置2个字符，总共180个字符
        board_positions = ["99"] * 90  # 初始化所有位置为空（99）

        # 遍历所有棋子，将其放置到对应位置
        for piece in self.pieces:
            x, y = piece['x'], piece['y']
            # 只处理在棋盘上的棋子（不是被吃掉的棋子）
            if x != 99 and y != 99 and 0 <= x < 9 and 0 <= y < 10:
                # 计算在90个位置中的索引（列行格式）
                pos_index = x * 10 + y
                # 在该位置标记棋子的当前坐标
                board_positions[pos_index] = f"{x:01d}{y:01d}"

        result = "".join(board_positions)
        print(f"DEBUG to_string: 生成棋盘状态长度={len(result)}, 内容前50字符={result[:50]}")
        return result
    
    def load_from_string(self, board_string):
        # 从180字符的棋盘状态字符串加载棋盘（与spark_chess_analysis.py兼容）
        print(f"DEBUG load_from_string: 输入棋盘状态长度={len(board_string)}, 前50字符={board_string[:50]}")

        if len(board_string) != 180:
            raise ValueError("棋盘字符串长度必须为180字符")

        # 验证字符串只包含数字
        if not board_string.isdigit():
            raise ValueError("棋盘字符串必须只包含数字")

        # 解析180字符的棋盘状态
        # 将180字符的字符串转换为90个位置的列表
        board_positions = []
        for i in range(0, 180, 2):
            board_positions.append(board_string[i:i+2])

        print(f"DEBUG load_from_string: 解析出{len(board_positions)}个位置")

        # 收集所有棋盘上的棋子位置
        pieces_on_board = []
        for pos_index, piece_coord in enumerate(board_positions):
            if piece_coord != "99":
                try:
                    x = int(piece_coord[0])
                    y = int(piece_coord[1])
                    if 0 <= x < 9 and 0 <= y < 10:
                        pieces_on_board.append((x, y))
                        print(f"DEBUG load_from_string: 发现棋子在位置 ({x},{y})")
                except (ValueError, IndexError):
                    continue

        print(f"DEBUG load_from_string: 棋盘上共有{len(pieces_on_board)}个棋子")

        # 重新创建棋子列表，基于实际棋盘状态
        self.pieces = []

        # 为每个棋盘上的位置创建棋子
        for x, y in pieces_on_board:
            # 根据位置推断棋子类型
            piece_info = self._identify_piece_at_position(x, y)
            if piece_info:
                self.pieces.append({
                    'name': piece_info['name'],
                    'x': x,
                    'y': y,
                    'type': piece_info['type']
                })
                print(f"DEBUG load_from_string: 创建棋子 {piece_info['type']} {piece_info['name']} 在位置 ({x},{y})")
            else:
                # 如果无法根据位置推断，使用通用方法
                # 根据y坐标判断是红方还是黑方
                piece_type = 'black' if y <= 4 else 'red'
                # 使用通用名称
                piece_name = '未知'

                # 尝试更精确的推断
                if y <= 4:  # 黑方区域
                    if y == 0:
                        piece_name = ['车', '马', '象', '士', '将', '士', '象', '马', '车'][x] if x < 9 else '未知'
                    elif y == 2 and (x == 1 or x == 7):
                        piece_name = '炮'
                    elif y == 3 and x in [0, 2, 4, 6, 8]:
                        piece_name = '卒'
                else:  # 红方区域
                    if y == 9:
                        piece_name = ['车', '马', '相', '仕', '帅', '仕', '相', '马', '车'][x] if x < 9 else '未知'
                    elif y == 7 and (x == 1 or x == 7):
                        piece_name = '炮'
                    elif y == 6 and x in [0, 2, 4, 6, 8]:
                        piece_name = '兵'

                self.pieces.append({
                    'name': piece_name,
                    'x': x,
                    'y': y,
                    'type': piece_type
                })
                print(f"DEBUG load_from_string: 创建推断棋子 {piece_type} {piece_name} 在位置 ({x},{y})")

        print(f"DEBUG load_from_string: 总共创建了{len(self.pieces)}个棋子")
        self.update_board()



    def _identify_piece_at_position(self, x, y):
        # 根据位置识别应该在该位置的棋子类型
        # 这是基于标准中国象棋初始布局的推断

        # 黑方棋子（上方，y=0-4）
        if y == 0:  # 第0行：黑方后排
            pieces = ['车', '马', '象', '士', '将', '士', '象', '马', '车']
            if 0 <= x < len(pieces):
                return {'name': pieces[x], 'type': 'black'}
        elif y == 2:  # 第2行：黑方炮
            if x == 1 or x == 7:
                return {'name': '炮', 'type': 'black'}
        elif y == 3:  # 第3行：黑方兵
            if x in [0, 2, 4, 6, 8]:
                return {'name': '卒', 'type': 'black'}

        # 红方棋子（下方，y=5-9）
        elif y == 6:  # 第6行：红方兵
            if x in [0, 2, 4, 6, 8]:
                return {'name': '兵', 'type': 'red'}
        elif y == 7:  # 第7行：红方炮
            if x == 1 or x == 7:
                return {'name': '炮', 'type': 'red'}
        elif y == 9:  # 第9行：红方后排
            pieces = ['车', '马', '相', '仕', '帅', '仕', '相', '马', '车']
            if 0 <= x < len(pieces):
                return {'name': pieces[x], 'type': 'red'}

        return None
