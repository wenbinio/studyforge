using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Microsoft.Data.Sqlite;
using StudyForge.Models;
using Newtonsoft.Json;

namespace StudyForge.Services
{
    /// <summary>
    /// Database service for persisting study data
    /// </summary>
    public class DatabaseService
    {
        private readonly string _connectionString;
        
        public DatabaseService()
        {
            var appDataPath = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
                "StudyForge");
            
            if (!Directory.Exists(appDataPath))
                Directory.CreateDirectory(appDataPath);
            
            var dbPath = Path.Combine(appDataPath, "studyforge.db");
            _connectionString = $"Data Source={dbPath}";
            
            InitializeDatabase();
        }
        
        private void InitializeDatabase()
        {
            using var connection = new SqliteConnection(_connectionString);
            connection.Open();
            
            var command = connection.CreateCommand();
            command.CommandText = @"
                CREATE TABLE IF NOT EXISTS Flashcards (
                    Id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Question TEXT NOT NULL,
                    Answer TEXT NOT NULL,
                    Notes TEXT,
                    Category TEXT NOT NULL,
                    NextReviewDate TEXT NOT NULL,
                    Repetitions INTEGER NOT NULL,
                    EaseFactor REAL NOT NULL,
                    Interval INTEGER NOT NULL,
                    CreatedDate TEXT NOT NULL,
                    LastReviewedDate TEXT NOT NULL,
                    GeneratedByAI INTEGER NOT NULL,
                    SourceMaterial TEXT
                );
                
                CREATE TABLE IF NOT EXISTS Notes (
                    Id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Title TEXT NOT NULL,
                    Content TEXT NOT NULL,
                    Category TEXT NOT NULL,
                    Tags TEXT,
                    CreatedDate TEXT NOT NULL,
                    ModifiedDate TEXT NOT NULL,
                    SourceFile TEXT,
                    IsCompleted INTEGER NOT NULL,
                    GeneratedFlashcardIds TEXT
                );
                
                CREATE TABLE IF NOT EXISTS PomodoroSessions (
                    Id INTEGER PRIMARY KEY AUTOINCREMENT,
                    StartTime TEXT NOT NULL,
                    EndTime TEXT,
                    CompletedPomodoros INTEGER NOT NULL,
                    Notes TEXT,
                    WorkDuration INTEGER NOT NULL,
                    ShortBreakDuration INTEGER NOT NULL,
                    LongBreakDuration INTEGER NOT NULL,
                    PomodorosUntilLongBreak INTEGER NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS Settings (
                    Key TEXT PRIMARY KEY,
                    Value TEXT NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS Statistics (
                    Id INTEGER PRIMARY KEY,
                    TotalCardsReviewed INTEGER NOT NULL,
                    TotalPomodorosCompleted INTEGER NOT NULL,
                    TotalStudyMinutes INTEGER NOT NULL,
                    CurrentStreak INTEGER NOT NULL,
                    LongestStreak INTEGER NOT NULL,
                    LastStudyDate TEXT,
                    CardsDueToday INTEGER NOT NULL,
                    CardsCreatedToday INTEGER NOT NULL
                );
                
                -- Insert default statistics if not exists
                INSERT OR IGNORE INTO Statistics (Id, TotalCardsReviewed, TotalPomodorosCompleted, 
                    TotalStudyMinutes, CurrentStreak, LongestStreak, CardsDueToday, CardsCreatedToday)
                VALUES (1, 0, 0, 0, 0, 0, 0, 0);
            ";
            
            command.ExecuteNonQuery();
        }
        
        // Flashcard Operations
        public void SaveFlashcard(Flashcard card)
        {
            using var connection = new SqliteConnection(_connectionString);
            connection.Open();
            
            var command = connection.CreateCommand();
            if (card.Id == 0)
            {
                command.CommandText = @"
                    INSERT INTO Flashcards (Question, Answer, Notes, Category, NextReviewDate, 
                        Repetitions, EaseFactor, Interval, CreatedDate, LastReviewedDate, 
                        GeneratedByAI, SourceMaterial)
                    VALUES (@Question, @Answer, @Notes, @Category, @NextReviewDate, 
                        @Repetitions, @EaseFactor, @Interval, @CreatedDate, @LastReviewedDate,
                        @GeneratedByAI, @SourceMaterial)
                ";
            }
            else
            {
                command.CommandText = @"
                    UPDATE Flashcards SET Question=@Question, Answer=@Answer, Notes=@Notes,
                        Category=@Category, NextReviewDate=@NextReviewDate, Repetitions=@Repetitions,
                        EaseFactor=@EaseFactor, Interval=@Interval, LastReviewedDate=@LastReviewedDate,
                        GeneratedByAI=@GeneratedByAI, SourceMaterial=@SourceMaterial
                    WHERE Id=@Id
                ";
                command.Parameters.AddWithValue("@Id", card.Id);
            }
            
            command.Parameters.AddWithValue("@Question", card.Question);
            command.Parameters.AddWithValue("@Answer", card.Answer);
            command.Parameters.AddWithValue("@Notes", card.Notes ?? (object)DBNull.Value);
            command.Parameters.AddWithValue("@Category", card.Category);
            command.Parameters.AddWithValue("@NextReviewDate", card.NextReviewDate.ToString("o"));
            command.Parameters.AddWithValue("@Repetitions", card.Repetitions);
            command.Parameters.AddWithValue("@EaseFactor", card.EaseFactor);
            command.Parameters.AddWithValue("@Interval", card.Interval);
            command.Parameters.AddWithValue("@CreatedDate", card.CreatedDate.ToString("o"));
            command.Parameters.AddWithValue("@LastReviewedDate", card.LastReviewedDate.ToString("o"));
            command.Parameters.AddWithValue("@GeneratedByAI", card.GeneratedByAI ? 1 : 0);
            command.Parameters.AddWithValue("@SourceMaterial", card.SourceMaterial ?? (object)DBNull.Value);
            
            command.ExecuteNonQuery();
        }
        
        public List<Flashcard> GetAllFlashcards()
        {
            var flashcards = new List<Flashcard>();
            
            using var connection = new SqliteConnection(_connectionString);
            connection.Open();
            
            var command = connection.CreateCommand();
            command.CommandText = "SELECT * FROM Flashcards ORDER BY NextReviewDate";
            
            using var reader = command.ExecuteReader();
            while (reader.Read())
            {
                flashcards.Add(ReadFlashcard(reader));
            }
            
            return flashcards;
        }
        
        public List<Flashcard> GetDueFlashcards()
        {
            var flashcards = new List<Flashcard>();
            
            using var connection = new SqliteConnection(_connectionString);
            connection.Open();
            
            var command = connection.CreateCommand();
            command.CommandText = @"
                SELECT * FROM Flashcards 
                WHERE NextReviewDate <= @Now
                ORDER BY NextReviewDate
            ";
            command.Parameters.AddWithValue("@Now", DateTime.Now.ToString("o"));
            
            using var reader = command.ExecuteReader();
            while (reader.Read())
            {
                flashcards.Add(ReadFlashcard(reader));
            }
            
            return flashcards;
        }
        
        public void DeleteFlashcard(int id)
        {
            using var connection = new SqliteConnection(_connectionString);
            connection.Open();
            
            var command = connection.CreateCommand();
            command.CommandText = "DELETE FROM Flashcards WHERE Id=@Id";
            command.Parameters.AddWithValue("@Id", id);
            command.ExecuteNonQuery();
        }
        
        private Flashcard ReadFlashcard(SqliteDataReader reader)
        {
            return new Flashcard
            {
                Id = reader.GetInt32(0),
                Question = reader.GetString(1),
                Answer = reader.GetString(2),
                Notes = reader.IsDBNull(3) ? null : reader.GetString(3),
                Category = reader.GetString(4),
                NextReviewDate = DateTime.Parse(reader.GetString(5)),
                Repetitions = reader.GetInt32(6),
                EaseFactor = reader.GetDouble(7),
                Interval = reader.GetInt32(8),
                CreatedDate = DateTime.Parse(reader.GetString(9)),
                LastReviewedDate = DateTime.Parse(reader.GetString(10)),
                GeneratedByAI = reader.GetInt32(11) == 1,
                SourceMaterial = reader.IsDBNull(12) ? null : reader.GetString(12)
            };
        }
        
        // Note Operations
        public void SaveNote(Note note)
        {
            using var connection = new SqliteConnection(_connectionString);
            connection.Open();
            
            var command = connection.CreateCommand();
            if (note.Id == 0)
            {
                command.CommandText = @"
                    INSERT INTO Notes (Title, Content, Category, Tags, CreatedDate, ModifiedDate,
                        SourceFile, IsCompleted, GeneratedFlashcardIds)
                    VALUES (@Title, @Content, @Category, @Tags, @CreatedDate, @ModifiedDate,
                        @SourceFile, @IsCompleted, @GeneratedFlashcardIds)
                ";
            }
            else
            {
                command.CommandText = @"
                    UPDATE Notes SET Title=@Title, Content=@Content, Category=@Category,
                        Tags=@Tags, ModifiedDate=@ModifiedDate, SourceFile=@SourceFile,
                        IsCompleted=@IsCompleted, GeneratedFlashcardIds=@GeneratedFlashcardIds
                    WHERE Id=@Id
                ";
                command.Parameters.AddWithValue("@Id", note.Id);
            }
            
            command.Parameters.AddWithValue("@Title", note.Title);
            command.Parameters.AddWithValue("@Content", note.Content);
            command.Parameters.AddWithValue("@Category", note.Category);
            command.Parameters.AddWithValue("@Tags", JsonConvert.SerializeObject(note.Tags));
            command.Parameters.AddWithValue("@CreatedDate", note.CreatedDate.ToString("o"));
            command.Parameters.AddWithValue("@ModifiedDate", DateTime.Now.ToString("o"));
            command.Parameters.AddWithValue("@SourceFile", note.SourceFile ?? (object)DBNull.Value);
            command.Parameters.AddWithValue("@IsCompleted", note.IsCompleted ? 1 : 0);
            command.Parameters.AddWithValue("@GeneratedFlashcardIds", JsonConvert.SerializeObject(note.GeneratedFlashcardIds));
            
            command.ExecuteNonQuery();
        }
        
        public List<Note> GetAllNotes()
        {
            var notes = new List<Note>();
            
            using var connection = new SqliteConnection(_connectionString);
            connection.Open();
            
            var command = connection.CreateCommand();
            command.CommandText = "SELECT * FROM Notes ORDER BY ModifiedDate DESC";
            
            using var reader = command.ExecuteReader();
            while (reader.Read())
            {
                notes.Add(ReadNote(reader));
            }
            
            return notes;
        }
        
        public void DeleteNote(int id)
        {
            using var connection = new SqliteConnection(_connectionString);
            connection.Open();
            
            var command = connection.CreateCommand();
            command.CommandText = "DELETE FROM Notes WHERE Id=@Id";
            command.Parameters.AddWithValue("@Id", id);
            command.ExecuteNonQuery();
        }
        
        private Note ReadNote(SqliteDataReader reader)
        {
            var tags = new List<string>();
            var flashcardIds = new List<int>();
            
            try
            {
                tags = JsonConvert.DeserializeObject<List<string>>(reader.GetString(4)) ?? new List<string>();
            }
            catch { }
            
            try
            {
                flashcardIds = JsonConvert.DeserializeObject<List<int>>(reader.GetString(9)) ?? new List<int>();
            }
            catch { }
            
            return new Note
            {
                Id = reader.GetInt32(0),
                Title = reader.GetString(1),
                Content = reader.GetString(2),
                Category = reader.GetString(3),
                Tags = tags,
                CreatedDate = DateTime.Parse(reader.GetString(5)),
                ModifiedDate = DateTime.Parse(reader.GetString(6)),
                SourceFile = reader.IsDBNull(7) ? null : reader.GetString(7),
                IsCompleted = reader.GetInt32(8) == 1,
                GeneratedFlashcardIds = flashcardIds
            };
        }
        
        // Statistics Operations
        public StudyStatistics GetStatistics()
        {
            using var connection = new SqliteConnection(_connectionString);
            connection.Open();
            
            var command = connection.CreateCommand();
            command.CommandText = "SELECT * FROM Statistics WHERE Id=1";
            
            using var reader = command.ExecuteReader();
            if (reader.Read())
            {
                return new StudyStatistics
                {
                    TotalCardsReviewed = reader.GetInt32(1),
                    TotalPomodorosCompleted = reader.GetInt32(2),
                    TotalStudyMinutes = reader.GetInt32(3),
                    CurrentStreak = reader.GetInt32(4),
                    LongestStreak = reader.GetInt32(5),
                    LastStudyDate = reader.IsDBNull(6) ? null : DateTime.Parse(reader.GetString(6)),
                    CardsDueToday = reader.GetInt32(7),
                    CardsCreatedToday = reader.GetInt32(8)
                };
            }
            
            return new StudyStatistics();
        }
        
        public void SaveStatistics(StudyStatistics stats)
        {
            using var connection = new SqliteConnection(_connectionString);
            connection.Open();
            
            var command = connection.CreateCommand();
            command.CommandText = @"
                UPDATE Statistics SET 
                    TotalCardsReviewed=@TotalCardsReviewed,
                    TotalPomodorosCompleted=@TotalPomodorosCompleted,
                    TotalStudyMinutes=@TotalStudyMinutes,
                    CurrentStreak=@CurrentStreak,
                    LongestStreak=@LongestStreak,
                    LastStudyDate=@LastStudyDate,
                    CardsDueToday=@CardsDueToday,
                    CardsCreatedToday=@CardsCreatedToday
                WHERE Id=1
            ";
            
            command.Parameters.AddWithValue("@TotalCardsReviewed", stats.TotalCardsReviewed);
            command.Parameters.AddWithValue("@TotalPomodorosCompleted", stats.TotalPomodorosCompleted);
            command.Parameters.AddWithValue("@TotalStudyMinutes", stats.TotalStudyMinutes);
            command.Parameters.AddWithValue("@CurrentStreak", stats.CurrentStreak);
            command.Parameters.AddWithValue("@LongestStreak", stats.LongestStreak);
            command.Parameters.AddWithValue("@LastStudyDate", stats.LastStudyDate?.ToString("o") ?? (object)DBNull.Value);
            command.Parameters.AddWithValue("@CardsDueToday", stats.CardsDueToday);
            command.Parameters.AddWithValue("@CardsCreatedToday", stats.CardsCreatedToday);
            
            command.ExecuteNonQuery();
        }
        
        // Settings Operations
        public void SaveSetting(string key, string value)
        {
            using var connection = new SqliteConnection(_connectionString);
            connection.Open();
            
            var command = connection.CreateCommand();
            command.CommandText = @"
                INSERT OR REPLACE INTO Settings (Key, Value)
                VALUES (@Key, @Value)
            ";
            command.Parameters.AddWithValue("@Key", key);
            command.Parameters.AddWithValue("@Value", value);
            
            command.ExecuteNonQuery();
        }
        
        public string? GetSetting(string key)
        {
            using var connection = new SqliteConnection(_connectionString);
            connection.Open();
            
            var command = connection.CreateCommand();
            command.CommandText = "SELECT Value FROM Settings WHERE Key=@Key";
            command.Parameters.AddWithValue("@Key", key);
            
            var result = command.ExecuteScalar();
            return result?.ToString();
        }
        
        // Pomodoro Session Operations
        public void SavePomodoroSession(PomodoroSession session)
        {
            using var connection = new SqliteConnection(_connectionString);
            connection.Open();
            
            var command = connection.CreateCommand();
            command.CommandText = @"
                INSERT INTO PomodoroSessions (StartTime, EndTime, CompletedPomodoros, Notes,
                    WorkDuration, ShortBreakDuration, LongBreakDuration, PomodorosUntilLongBreak)
                VALUES (@StartTime, @EndTime, @CompletedPomodoros, @Notes,
                    @WorkDuration, @ShortBreakDuration, @LongBreakDuration, @PomodorosUntilLongBreak)
            ";
            
            command.Parameters.AddWithValue("@StartTime", session.StartTime.ToString("o"));
            command.Parameters.AddWithValue("@EndTime", session.EndTime?.ToString("o") ?? (object)DBNull.Value);
            command.Parameters.AddWithValue("@CompletedPomodoros", session.CompletedPomodoros);
            command.Parameters.AddWithValue("@Notes", session.Notes ?? (object)DBNull.Value);
            command.Parameters.AddWithValue("@WorkDuration", session.WorkDuration);
            command.Parameters.AddWithValue("@ShortBreakDuration", session.ShortBreakDuration);
            command.Parameters.AddWithValue("@LongBreakDuration", session.LongBreakDuration);
            command.Parameters.AddWithValue("@PomodorosUntilLongBreak", session.PomodorosUntilLongBreak);
            
            command.ExecuteNonQuery();
        }
    }
}
