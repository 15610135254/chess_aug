def validate_move_request(data):
    """
    验证移动请求数据
    支持180字符格式（9列×10行×2字符每位置）与spark_chess_analysis.py兼容
    """
    if not data:
        return {'valid': False, 'message': '请求数据为空'}

    if 'board' not in data:
        return {'valid': False, 'message': '缺少棋盘状态参数'}

    if 'move' not in data:
        return {'valid': False, 'message': '缺少移动参数'}

    board = data['board']
    move = data['move']

    # 验证棋盘字符串格式
    if not isinstance(board, str):
        return {'valid': False, 'message': '棋盘状态必须是字符串'}

    # 只支持180字符格式（与spark_chess_analysis.py兼容）
    if len(board) != 180:
        return {'valid': False, 'message': '棋盘状态字符串长度必须为180字符'}

    if not board.isdigit():
        return {'valid': False, 'message': '棋盘状态字符串必须全为数字'}

    # 验证移动字符串格式
    if not isinstance(move, str):
        return {'valid': False, 'message': '移动参数必须是字符串'}

    if len(move) != 4:
        return {'valid': False, 'message': '移动参数长度必须为4'}

    if not move.isdigit():
        return {'valid': False, 'message': '移动参数必须全为数字'}

    # 验证坐标范围（9列×10行坐标系统：00-89）
    try:
        from_x = int(move[0])
        from_y = int(move[1])
        to_x = int(move[2])
        to_y = int(move[3])

        # 坐标范围：列0-8，行0-9
        if not (0 <= from_x <= 8 and 0 <= from_y <= 9):
            return {'valid': False, 'message': '起始坐标超出范围（列0-8，行0-9）'}

        if not (0 <= to_x <= 8 and 0 <= to_y <= 9):
            return {'valid': False, 'message': '目标坐标超出范围（列0-8，行0-9）'}

    except ValueError:
        return {'valid': False, 'message': '坐标格式错误'}

    return {'valid': True, 'message': '验证通过'}
