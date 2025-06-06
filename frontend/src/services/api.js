import axios from 'axios'

const API_BASE_URL = 'http://localhost:5001/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

export const chessAPI = {
  // 初始化棋盘
  initBoard: async () => {
    try {
      const response = await api.get('/init')
      return response.data
    } catch (error) {
      console.error('初始化棋盘失败:', error)
      throw error
    }
  },

  // 移动棋子
  movePiece: async (board, move) => {
    try {
      const response = await api.post('/move', { board, move })
      return response.data
    } catch (error) {
      console.error('移动棋子失败:', error)
      throw error
    }
  },

  // 验证移动
  validateMove: async (board, move) => {
    try {
      const response = await api.post('/validate', { board, move })
      return response.data
    } catch (error) {
      console.error('验证移动失败:', error)
      throw error
    }
  },

  // 获取AI走法建议
  getAISuggestion: async (board, side = 'red') => {
    try {
      const response = await api.post('/ai/suggest', { board, side })
      return response.data
    } catch (error) {
      console.error('获取AI建议失败:', error)
      throw error
    }
  },

  // 执行AI自动移动
  executeAIMove: async (board, player = 'black') => {
    try {
      const response = await api.post('/ai/execute_move', { board, player })
      return response.data
    } catch (error) {
      console.error('执行AI移动失败:', error)
      throw error
    }
  },

  // 黑方自动移动
  blackAutoMove: async (board) => {
    try {
      const response = await api.post('/ai/black_auto_move', { board })
      return response.data
    } catch (error) {
      console.error('黑方自动移动失败:', error)
      throw error
    }
  }
}
