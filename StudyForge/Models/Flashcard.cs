using System;

namespace StudyForge.Models
{
    /// <summary>
    /// Represents a flashcard with spaced repetition scheduling
    /// </summary>
    public class Flashcard
    {
        public int Id { get; set; }
        public string Question { get; set; } = string.Empty;
        public string Answer { get; set; } = string.Empty;
        public string? Notes { get; set; }
        public string Category { get; set; } = "General";
        
        // Spaced Repetition (SM-2 Algorithm) Properties
        public DateTime NextReviewDate { get; set; }
        public int Repetitions { get; set; }
        public double EaseFactor { get; set; } = 2.5;
        public int Interval { get; set; }
        
        public DateTime CreatedDate { get; set; }
        public DateTime LastReviewedDate { get; set; }
        
        // AI Generation tracking
        public bool GeneratedByAI { get; set; }
        public string? SourceMaterial { get; set; }
        
        public Flashcard()
        {
            CreatedDate = DateTime.Now;
            NextReviewDate = DateTime.Now;
            LastReviewedDate = DateTime.MinValue;
        }
        
        /// <summary>
        /// Updates the card schedule based on user performance (SM-2 algorithm)
        /// </summary>
        /// <param name="quality">Quality of recall (0-5): 0=complete blackout, 5=perfect recall</param>
        public void UpdateSchedule(int quality)
        {
            if (quality < 0 || quality > 5)
                throw new ArgumentException("Quality must be between 0 and 5");
            
            LastReviewedDate = DateTime.Now;
            
            if (quality < 3)
            {
                // Reset the card if recall was poor
                Repetitions = 0;
                Interval = 1;
            }
            else
            {
                if (Repetitions == 0)
                {
                    Interval = 1;
                }
                else if (Repetitions == 1)
                {
                    Interval = 6;
                }
                else
                {
                    Interval = (int)Math.Round(Interval * EaseFactor);
                }
                
                Repetitions++;
            }
            
            // Update ease factor
            EaseFactor = EaseFactor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02));
            
            if (EaseFactor < 1.3)
                EaseFactor = 1.3;
            
            NextReviewDate = DateTime.Now.AddDays(Interval);
        }
    }
}
