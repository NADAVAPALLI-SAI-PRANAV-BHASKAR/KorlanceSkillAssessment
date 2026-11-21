/**
 * KORLANCE Examination Engine
 * Question navigation, palette status management, response autosaving, and server-synced countdown timer.
 */

class KorlanceExamEngine {
  constructor(options) {
    this.sessionToken = options.sessionToken;
    this.csrfToken = options.csrfToken;
    this.questions = options.questions || [];
    this.remainingSeconds = options.remainingSeconds || 2400; // 40 minutes
    this.currentIndex = 0;
    
    // UI Elements
    this.qNumberEl = document.getElementById('currentQuestionNumber');
    this.qDifficultyEl = document.getElementById('currentQuestionDifficulty');
    this.qTextEl = document.getElementById('currentQuestionText');
    this.optionsContainer = document.getElementById('optionsContainer');
    this.timerDisplayEl = document.getElementById('examTimerDisplay');
    
    // Summary Counters
    this.paletteContainer = document.getElementById('questionPaletteGrid');
    this.answeredCountEl = document.getElementById('summaryAnsweredCount');
    this.unansweredCountEl = document.getElementById('summaryUnansweredCount');
    this.markedCountEl = document.getElementById('summaryMarkedCount');

    // Buttons
    this.prevBtn = document.getElementById('btnPrevious');
    this.saveNextBtn = document.getElementById('btnSaveNext');
    this.markReviewBtn = document.getElementById('btnMarkReview');
    this.clearBtn = document.getElementById('btnClear');
    this.openSubmitModalBtn = document.getElementById('btnOpenSubmitModal');

    this.timerInterval = null;
    this.init();
  }

  init() {
    this.renderPalette();
    this.loadQuestion(0);
    this.startCountdown();
    this.bindEvents();
    this.updateSummaryCounts();
  }

  bindEvents() {
    if (this.prevBtn) {
      this.prevBtn.addEventListener('click', () => {
        if (this.currentIndex > 0) {
          this.loadQuestion(this.currentIndex - 1);
        }
      });
    }

    if (this.saveNextBtn) {
      this.saveNextBtn.addEventListener('click', () => {
        this.saveCurrentSelection(false);
        if (this.currentIndex < this.questions.length - 1) {
          this.loadQuestion(this.currentIndex + 1);
        }
      });
    }

    if (this.markReviewBtn) {
      this.markReviewBtn.addEventListener('click', () => {
        const q = this.questions[this.currentIndex];
        q.marked_for_review = !q.marked_for_review;
        this.saveCurrentSelection(q.marked_for_review);
        if (this.currentIndex < this.questions.length - 1) {
          this.loadQuestion(this.currentIndex + 1);
        } else {
          this.updatePaletteButton(this.currentIndex);
          this.updateSummaryCounts();
        }
      });
    }

    if (this.clearBtn) {
      this.clearBtn.addEventListener('click', () => {
        const q = this.questions[this.currentIndex];
        q.selected = '';
        const radios = this.optionsContainer.querySelectorAll('input[type="radio"]');
        radios.forEach(r => r.checked = false);
        this.saveAnswerToServer(q.id, 'CLEAR', q.marked_for_review);
        this.updatePaletteButton(this.currentIndex);
        this.updateSummaryCounts();
      });
    }

    if (this.openSubmitModalBtn) {
      this.openSubmitModalBtn.addEventListener('click', () => {
        this.populateSubmitModal();
        const modal = document.getElementById('submitConfirmModal');
        if (modal) modal.classList.remove('hidden');
      });
    }

    const cancelSubmitBtn = document.getElementById('btnCancelSubmit');
    if (cancelSubmitBtn) {
      cancelSubmitBtn.addEventListener('click', () => {
        const modal = document.getElementById('submitConfirmModal');
        if (modal) modal.classList.add('hidden');
      });
    }
  }

  startCountdown() {
    this.updateTimerDisplay();

    this.timerInterval = setInterval(() => {
      this.remainingSeconds--;
      this.updateTimerDisplay();

      if (this.remainingSeconds <= 0) {
        clearInterval(this.timerInterval);
        this.autoSubmitOnTimeout();
      }
    }, 1000);
  }

  updateTimerDisplay() {
    if (!this.timerDisplayEl) return;
    const mins = Math.floor(Math.max(0, this.remainingSeconds) / 60);
    const secs = Math.max(0, this.remainingSeconds) % 60;
    const formatted = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    this.timerDisplayEl.textContent = formatted;

    // Visual warning when under 5 minutes
    if (this.remainingSeconds < 300) {
      this.timerDisplayEl.classList.add('text-rose-600', 'animate-pulse');
      this.timerDisplayEl.classList.remove('text-slate-900');
    }
  }

  loadQuestion(index) {
    this.currentIndex = index;
    const q = this.questions[index];
    q.visited = true;

    // Update Header
    if (this.qNumberEl) this.qNumberEl.textContent = `Question ${q.order} of ${this.questions.length}`;
    if (this.qDifficultyEl) {
      this.qDifficultyEl.textContent = q.difficulty;
      if (q.difficulty === 'EASY') {
        this.qDifficultyEl.className = 'px-2 py-0.5 rounded text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200';
      } else if (q.difficulty === 'MEDIUM') {
        this.qDifficultyEl.className = 'px-2 py-0.5 rounded text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200';
      } else {
        this.qDifficultyEl.className = 'px-2 py-0.5 rounded text-xs font-semibold bg-purple-50 text-purple-700 border border-purple-200';
      }
    }

    // Question Stem
    if (this.qTextEl) this.qTextEl.textContent = q.text;

    // Options Rendering
    if (this.optionsContainer) {
      this.optionsContainer.innerHTML = '';
      const opts = q.options;

      ['A', 'B', 'C', 'D'].forEach(key => {
        const optText = opts[key];
        const isChecked = (q.selected === key);

        const label = document.createElement('label');
        label.className = `flex items-start gap-3.5 p-4 rounded-xl border cursor-pointer transition-all ${
          isChecked 
            ? 'bg-purple-50 border-purple-400 ring-1 ring-purple-400 shadow-sm' 
            : 'bg-white border-slate-200 hover:bg-slate-50 hover:border-slate-300'
        }`;

        label.innerHTML = `
          <input type="radio" name="opt_choice" value="${key}" ${isChecked ? 'checked' : ''} class="mt-1 text-purple-600 focus:ring-purple-500 w-4 h-4 border-slate-300">
          <div class="flex-1 text-sm font-medium text-slate-800 leading-relaxed">
            <span class="inline-block font-bold text-purple-900 mr-1.5">${key}.</span>
            ${optText}
          </div>
        `;

        label.querySelector('input').addEventListener('change', (e) => {
          if (e.target.checked) {
            q.selected = key;
            this.updatePaletteButton(this.currentIndex);
            this.updateSummaryCounts();
            this.saveAnswerToServer(q.id, key, q.marked_for_review);
            
            // Re-render labels style
            const allLabels = this.optionsContainer.querySelectorAll('label');
            allLabels.forEach(l => {
              l.className = 'flex items-start gap-3.5 p-4 rounded-xl border cursor-pointer transition-all bg-white border-slate-200 hover:bg-slate-50';
            });
            label.className = 'flex items-start gap-3.5 p-4 rounded-xl border cursor-pointer transition-all bg-purple-50 border-purple-400 ring-1 ring-purple-400 shadow-sm';
          }
        });

        this.optionsContainer.appendChild(label);
      });
    }

    // Previous Button Disabled on First Question
    if (this.prevBtn) {
      this.prevBtn.disabled = (this.currentIndex === 0);
      this.prevBtn.classList.toggle('opacity-50', this.currentIndex === 0);
      this.prevBtn.classList.toggle('cursor-not-allowed', this.currentIndex === 0);
    }

    this.updatePaletteButton(index);
    this.updateSummaryCounts();
  }

  saveCurrentSelection(isMarkedForReview) {
    const q = this.questions[this.currentIndex];
    q.marked_for_review = isMarkedForReview;
    const selectedRadio = this.optionsContainer.querySelector('input[type="radio"]:checked');
    if (selectedRadio) {
      q.selected = selectedRadio.value;
    }
    this.saveAnswerToServer(q.id, q.selected || null, q.marked_for_review);
    this.updatePaletteButton(this.currentIndex);
    this.updateSummaryCounts();
  }

  async saveAnswerToServer(questionId, selectedOption, isMarkedForReview) {
    try {
      await fetch('/exam/save-answer/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.csrfToken
        },
        body: JSON.stringify({
          session_token: this.sessionToken,
          question_id: questionId,
          selected_option: selectedOption,
          is_marked_for_review: isMarkedForReview,
          is_visited: true
        })
      });
    } catch (e) {
      console.warn('Network autosave error:', e);
    }
  }

  renderPalette() {
    if (!this.paletteContainer) return;
    this.paletteContainer.innerHTML = '';

    this.questions.forEach((q, idx) => {
      const btn = document.createElement('div');
      btn.id = `palette-item-${idx}`;
      btn.textContent = q.order;
      btn.className = `palette-btn ${this.getQuestionStatusClass(q)}`;
      btn.addEventListener('click', () => {
        this.saveCurrentSelection(this.questions[this.currentIndex].marked_for_review);
        this.loadQuestion(idx);
      });
      this.paletteContainer.appendChild(btn);
    });
  }

  updatePaletteButton(idx) {
    const btn = document.getElementById(`palette-item-${idx}`);
    if (!btn) return;
    const q = this.questions[idx];

    // Remove status classes
    btn.className = `palette-btn ${this.getQuestionStatusClass(q)}`;
    if (idx === this.currentIndex) {
      btn.classList.add('active-q');
    }
  }

  getQuestionStatusClass(q) {
    // 5 status conditions:
    // 1. Answered & Marked for Review
    if (q.selected && q.marked_for_review) return 'status-answered-review';
    // 2. Answered
    if (q.selected) return 'status-answered';
    // 3. Marked for Review (Unanswered)
    if (q.marked_for_review) return 'status-review';
    // 4. Not Answered (visited, but not answered)
    if (q.visited) return 'status-unanswered';
    // 5. Not Visited
    return 'status-unvisited';
  }

  updateSummaryCounts() {
    let answered = 0;
    let marked = 0;
    let notVisited = 0;

    this.questions.forEach(q => {
      if (q.selected) answered++;
      if (q.marked_for_review) marked++;
      if (!q.visited) notVisited++;
    });

    const unanswered = this.questions.length - answered;

    if (this.answeredCountEl) this.answeredCountEl.textContent = answered;
    if (this.unansweredCountEl) this.unansweredCountEl.textContent = unanswered;
    if (this.markedCountEl) this.markedCountEl.textContent = marked;
  }

  populateSubmitModal() {
    let answered = 0;
    let marked = 0;
    this.questions.forEach(q => {
      if (q.selected) answered++;
      if (q.marked_for_review) marked++;
    });
    const unanswered = this.questions.length - answered;

    const modalAnsEl = document.getElementById('modalAnsweredCount');
    const modalUnansEl = document.getElementById('modalUnansweredCount');
    const modalMarkedEl = document.getElementById('modalMarkedCount');

    if (modalAnsEl) modalAnsEl.textContent = answered;
    if (modalUnansEl) modalUnansEl.textContent = unanswered;
    if (modalMarkedEl) modalMarkedEl.textContent = marked;
  }

  autoSubmitOnTimeout() {
    const form = document.getElementById('examSubmitForm');
    if (form) {
      const typeInput = form.querySelector('input[name="submission_type"]');
      if (typeInput) typeInput.value = 'AUTO_TIMEOUT';
      form.submit();
    }
  }
}

window.KorlanceExamEngine = KorlanceExamEngine;
