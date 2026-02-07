using System;
using System.Windows.Threading;
using StudyForge.Models;

namespace StudyForge.Services
{
    /// <summary>
    /// Service for managing Pomodoro timer functionality
    /// </summary>
    public class PomodoroService
    {
        private DispatcherTimer? _timer;
        private PomodoroSession _currentSession;
        private PomodoroState _currentState;
        private TimeSpan _remainingTime;
        
        public event EventHandler<PomodoroState>? StateChanged;
        public event EventHandler<TimeSpan>? TimeUpdated;
        public event EventHandler? IntervalCompleted;
        
        public PomodoroState CurrentState => _currentState;
        public TimeSpan RemainingTime => _remainingTime;
        public PomodoroSession CurrentSession => _currentSession;
        
        public PomodoroService()
        {
            _currentSession = new PomodoroSession();
            _currentState = PomodoroState.Ready;
            _remainingTime = TimeSpan.FromMinutes(_currentSession.WorkDuration);
        }
        
        public void Start()
        {
            if (_timer == null)
            {
                _timer = new DispatcherTimer();
                _timer.Interval = TimeSpan.FromSeconds(1);
                _timer.Tick += Timer_Tick;
            }
            
            if (_currentState == PomodoroState.Ready)
            {
                _currentState = PomodoroState.Work;
                _remainingTime = TimeSpan.FromMinutes(_currentSession.WorkDuration);
                StateChanged?.Invoke(this, _currentState);
            }
            else if (_currentState == PomodoroState.Paused)
            {
                // Resume from pause
                var previousState = _currentState;
                StateChanged?.Invoke(this, _currentState);
            }
            
            _timer.Start();
        }
        
        public void Pause()
        {
            if (_timer != null && _timer.IsEnabled)
            {
                _timer.Stop();
                _currentState = PomodoroState.Paused;
                StateChanged?.Invoke(this, _currentState);
            }
        }
        
        public void Reset()
        {
            _timer?.Stop();
            _currentSession = new PomodoroSession();
            _currentState = PomodoroState.Ready;
            _remainingTime = TimeSpan.FromMinutes(_currentSession.WorkDuration);
            StateChanged?.Invoke(this, _currentState);
            TimeUpdated?.Invoke(this, _remainingTime);
        }
        
        public void Skip()
        {
            CompleteCurrentInterval();
        }
        
        public void Configure(int workMinutes, int shortBreakMinutes, int longBreakMinutes, int pomodorosUntilLongBreak)
        {
            _currentSession.WorkDuration = workMinutes;
            _currentSession.ShortBreakDuration = shortBreakMinutes;
            _currentSession.LongBreakDuration = longBreakMinutes;
            _currentSession.PomodorosUntilLongBreak = pomodorosUntilLongBreak;
            
            if (_currentState == PomodoroState.Ready)
            {
                _remainingTime = TimeSpan.FromMinutes(workMinutes);
                TimeUpdated?.Invoke(this, _remainingTime);
            }
        }
        
        private void Timer_Tick(object? sender, EventArgs e)
        {
            _remainingTime = _remainingTime.Subtract(TimeSpan.FromSeconds(1));
            TimeUpdated?.Invoke(this, _remainingTime);
            
            if (_remainingTime.TotalSeconds <= 0)
            {
                CompleteCurrentInterval();
            }
        }
        
        private void CompleteCurrentInterval()
        {
            _timer?.Stop();
            
            switch (_currentState)
            {
                case PomodoroState.Work:
                    _currentSession.CompletedPomodoros++;
                    
                    // Determine next break type
                    if (_currentSession.CompletedPomodoros % _currentSession.PomodorosUntilLongBreak == 0)
                    {
                        _currentState = PomodoroState.LongBreak;
                        _remainingTime = TimeSpan.FromMinutes(_currentSession.LongBreakDuration);
                    }
                    else
                    {
                        _currentState = PomodoroState.ShortBreak;
                        _remainingTime = TimeSpan.FromMinutes(_currentSession.ShortBreakDuration);
                    }
                    break;
                    
                case PomodoroState.ShortBreak:
                case PomodoroState.LongBreak:
                    _currentState = PomodoroState.Work;
                    _remainingTime = TimeSpan.FromMinutes(_currentSession.WorkDuration);
                    break;
            }
            
            IntervalCompleted?.Invoke(this, EventArgs.Empty);
            StateChanged?.Invoke(this, _currentState);
            TimeUpdated?.Invoke(this, _remainingTime);
        }
        
        public void EndSession(DatabaseService database)
        {
            _currentSession.EndTime = DateTime.Now;
            database.SavePomodoroSession(_currentSession);
            
            // Update statistics
            var stats = database.GetStatistics();
            stats.TotalPomodorosCompleted += _currentSession.CompletedPomodoros;
            stats.UpdateStreak();
            database.SaveStatistics(stats);
        }
    }
}
