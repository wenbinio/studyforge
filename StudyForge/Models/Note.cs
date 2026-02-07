using System;
using System.Collections.Generic;

namespace StudyForge.Models
{
    /// <summary>
    /// Represents a study note or lecture material
    /// </summary>
    public class Note
    {
        public int Id { get; set; }
        public string Title { get; set; } = string.Empty;
        public string Content { get; set; } = string.Empty;
        public string Category { get; set; } = "General";
        public List<string> Tags { get; set; } = new List<string>();
        public DateTime CreatedDate { get; set; }
        public DateTime ModifiedDate { get; set; }
        public string? SourceFile { get; set; }
        public bool IsCompleted { get; set; }
        
        // Track which flashcards were generated from this note
        public List<int> GeneratedFlashcardIds { get; set; } = new List<int>();
        
        public Note()
        {
            CreatedDate = DateTime.Now;
            ModifiedDate = DateTime.Now;
        }
    }
}
