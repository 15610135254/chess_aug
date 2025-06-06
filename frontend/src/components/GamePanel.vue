<template>
  <div class="game-panel">
    <div class="game-info">
      <h2>中国象棋</h2>
      
      <div class="current-player">
        <span class="label">当前回合:</span>
        <span :class="['player', currentPlayer]">
          {{ currentPlayer === 'red' ? '红方(人类)' : '黑方(AI)' }}
        </span>
      </div>
      
      <div v-if="aiThinking" class="ai-thinking">
        <span class="label">AI思考中:</span>
        <div class="thinking-indicator">
          <div class="dot"></div>
          <div class="dot"></div>
          <div class="dot"></div>
        </div>
      </div>
      
      <div v-if="selectedPiece && selectedPiece.piece" class="selected-piece">
        <span class="label">已选择:</span>
        <span :class="['piece', selectedPiece.piece.type]">
          {{ selectedPiece.piece.name }}
        </span>
        <span class="position">
          ({{ selectedPiece.x }}, {{ selectedPiece.y }})
        </span>
      </div>
      
      <div v-if="error" class="error-message">
        {{ error }}
      </div>
      
      <div v-if="loading" class="loading">
        游戏处理中...
      </div>
    </div>
    
    <div class="game-controls">
      <button
        @click="$emit('restart')"
        :disabled="loading"
        class="btn btn-primary"
      >
        重新开始
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  currentPlayer: {
    type: String,
    default: 'red'
  },
  selectedPiece: {
    type: Object,
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: ''
  },
  gameOver: {
    type: Boolean,
    default: false
  },
  winner: {
    type: String,
    default: ''
  },
  aiThinking: {
    type: Boolean,
    default: false
  },
  gameMode: {
    type: String,
    default: 'human_vs_ai'
  }
})

defineEmits(['restart'])
</script>

<style scoped>
.game-panel {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  min-width: 280px;
  width: 320px;
  height: fit-content;
}

.game-info h2 {
  margin: 0 0 20px 0;
  color: #333;
  text-align: center;
  font-size: 24px;
}

.current-player,
.selected-piece,
.game-stats .stat {
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.label {
  font-weight: bold;
  color: #666;
  min-width: 80px;
}

.player.red,
.piece.red {
  color: #d32f2f;
  font-weight: bold;
}

.player.black,
.piece.black {
  color: #1976d2;
  font-weight: bold;
}

.position {
  color: #999;
  font-size: 14px;
}

.error-message {
  background: #ffebee;
  color: #c62828;
  padding: 8px 12px;
  border-radius: 4px;
  margin-bottom: 15px;
  font-size: 14px;
}

.loading {
  background: #e3f2fd;
  color: #1976d2;
  padding: 8px 12px;
  border-radius: 4px;
  margin-bottom: 15px;
  font-size: 14px;
  text-align: center;
}

.game-controls {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin: 20px 0;
}

.btn {
  padding: 10px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: bold;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: #1976d2;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #1565c0;
}

.btn-secondary {
  background: #757575;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #616161;
}

.game-stats {
  border-top: 1px solid #eee;
  padding-top: 15px;
}

.value {
  font-weight: bold;
  color: #333;
}

.ai-thinking {
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fff3e0;
  padding: 8px 12px;
  border-radius: 4px;
  border-left: 4px solid #ff9800;
}

.thinking-indicator {
  display: flex;
  gap: 4px;
  align-items: center;
}

.dot {
  width: 6px;
  height: 6px;
  background: #ff9800;
  border-radius: 50%;
  animation: thinking 1.4s infinite both;
}

.dot:nth-child(1) {
  animation-delay: -0.32s;
}

.dot:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes thinking {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}
</style>
