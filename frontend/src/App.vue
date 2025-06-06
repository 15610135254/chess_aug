<script setup>
import { onMounted } from 'vue'
import ChessBoard from './components/ChessBoard.vue'
import GamePanel from './components/GamePanel.vue'
import AISuggestion from './components/AISuggestion.vue'
import { useChessGame } from './composables/useChessGame.js'

const {
  pieces,
  currentPlayer,
  selectedPiece,
  gameOver,
  winner,
  loading,
  error,
  boardString,
  aiThinking,
  gameMode,
  BOARD_WIDTH,
  BOARD_HEIGHT,
  CELL_SIZE,
  initGame,
  handleBoardClick,
  restartGame,
  isAITurn
} = useChessGame()

onMounted(() => {
  initGame()
})
</script>

<template>
  <div class="app">
    <header class="app-header">
      <h1>中国象棋游戏</h1>
    </header>

    <main class="app-main">
      <div class="game-container">
        <ChessBoard
          :pieces="pieces"
          :selected-piece="selectedPiece"
          :board-width="BOARD_WIDTH"
          :board-height="BOARD_HEIGHT"
          :cell-size="CELL_SIZE"
          @board-click="handleBoardClick"
        />

        <div class="right-panel">
          <GamePanel
            :current-player="currentPlayer"
            :selected-piece="selectedPiece"
            :loading="loading"
            :error="error"
            :game-over="gameOver"
            :winner="winner"
            :ai-thinking="aiThinking"
            :game-mode="gameMode"
            @restart="restartGame"
          />
          
          <AISuggestion
            :board-string="boardString"
            :current-player="currentPlayer"
            :game-over="gameOver"
            :auto-suggest="true"
          />
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.app {
  min-height: 100vh;
  width: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  box-sizing: border-box;
}

.app-header {
  text-align: center;
  margin-bottom: 30px;
}

.app-header h1 {
  color: white;
  font-size: 2.5rem;
  margin: 0;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.app-main {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  width: 100%;
}

.game-container {
  display: flex;
  gap: 30px;
  align-items: flex-start;
  width: 100%;
  max-width: 1200px;
  justify-content: center;
}

.right-panel {
  width: 300px;
  min-width: 280px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

@media (max-width: 1200px) {
  .game-container {
    gap: 20px;
  }
  
  .right-panel {
    width: 250px;
    min-width: 250px;
  }
}

@media (max-width: 900px) {
  .game-container {
    flex-direction: column;
    align-items: center;
  }
  
  .right-panel {
    width: 100%;
    max-width: 500px;
  }

  .app-header h1 {
    font-size: 2rem;
  }
}
</style>
