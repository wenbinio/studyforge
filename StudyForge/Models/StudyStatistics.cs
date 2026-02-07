using System;

namespace StudyForge.Models
{
    /// <summary>
    /// Represents study statistics and progress tracking
    /// </summary>
    public class StudyStatistics
    {
        public int TotalCardsReviewed { get; set; }
        public int TotalPomodorosCompleted { get; set; }
        public int TotalStudyMinutes { get; set; }
        public int CurrentStreak { get; set; }
        public int LongestStreak { get; set; }
        public DateTime? LastStudyDate { get; set; }
        public int CardsDueToday { get; set; }
        public int CardsCreatedToday { get; set; }
        
        public void UpdateStreak()
        {
            if (LastStudyDate.HasValue)
            {
                var daysSinceLastStudy = (DateTime.Now.Date - LastStudyDate.Value.Date).Days;
                if (daysSinceLastStudy == 1)
                {
                    CurrentStreak++;
                    if (CurrentStreak > LongestStreak)
                        LongestStreak = CurrentStreak;
                }
                else if (daysSinceLastStudy > 1)
                {
                    CurrentStreak = 1;
                }
            }
            else
            {
                CurrentStreak = 1;
            }
            
            LastStudyDate = DateTime.Now;
        }
    }
}
