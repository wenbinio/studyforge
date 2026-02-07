using System;

namespace StudyForge.Models
{
    public enum PomodoroState
    {
        Ready,
        Work,
        ShortBreak,
        LongBreak,
        Paused
    }
    
    /// <summary>
    /// Represents a Pomodoro study session
    /// </summary>
    public class PomodoroSession
    {
        public int Id { get; set; }
        public DateTime StartTime { get; set; }
        public DateTime? EndTime { get; set; }
        public int CompletedPomodoros { get; set; }
        public string? Notes { get; set; }
        
        // Configuration
        public int WorkDuration { get; set; } = 25; // minutes
        public int ShortBreakDuration { get; set; } = 5; // minutes
        public int LongBreakDuration { get; set; } = 15; // minutes
        public int PomodorosUntilLongBreak { get; set; } = 4;
        
        public PomodoroSession()
        {
            StartTime = DateTime.Now;
        }
    }
    
    /// <summary>
    /// Represents a single pomodoro interval
    /// </summary>
    public class PomodoroInterval
    {
        public int Id { get; set; }
        public int SessionId { get; set; }
        public DateTime StartTime { get; set; }
        public DateTime? EndTime { get; set; }
        public PomodoroState State { get; set; }
        public bool Completed { get; set; }
        
        public PomodoroInterval()
        {
            StartTime = DateTime.Now;
        }
    }
}
