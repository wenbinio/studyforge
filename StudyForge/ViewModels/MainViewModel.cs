using System;
using System.Collections.ObjectModel;
using System.Linq;
using System.Windows;
using System.Windows.Input;
using StudyForge.Models;
using StudyForge.Services;

namespace StudyForge.ViewModels
{
    public class MainViewModel : ViewModelBase
    {
        private readonly DatabaseService _database;
        private readonly ClaudeApiService _claudeApi;
        private readonly PomodoroService _pomodoro;
        
        private string _currentView = "Dashboard";
        private string _pomodoroTimeDisplay = "25:00";
        private string _pomodoroStateDisplay = "Ready";
        private StudyStatistics _statistics;
        
        public string CurrentView
        {
            get => _currentView;
            set => SetProperty(ref _currentView, value);
        }
        
        public string PomodoroTimeDisplay
        {
            get => _pomodoroTimeDisplay;
            set => SetProperty(ref _pomodoroTimeDisplay, value);
        }
        
        public string PomodoroStateDisplay
        {
            get => _pomodoroStateDisplay;
            set => SetProperty(ref _pomodoroStateDisplay, value);
        }
        
        public StudyStatistics Statistics
        {
            get => _statistics;
            set => SetProperty(ref _statistics, value);
        }
        
        public ObservableCollection<Flashcard> Flashcards { get; }
        public ObservableCollection<Flashcard> DueFlashcards { get; }
        public ObservableCollection<Note> Notes { get; }
        
        // Commands
        public ICommand NavigateToDashboardCommand { get; }
        public ICommand NavigateToFlashcardsCommand { get; }
        public ICommand NavigateToNotesCommand { get; }
        public ICommand NavigateToPomodoroCommand { get; }
        public ICommand NavigateToSettingsCommand { get; }
        public ICommand StartPomodoroCommand { get; }
        public ICommand PausePomodoroCommand { get; }
        public ICommand ResetPomodoroCommand { get; }
        
        public MainViewModel()
        {
            _database = new DatabaseService();
            _claudeApi = new ClaudeApiService();
            _pomodoro = new PomodoroService();
            _statistics = _database.GetStatistics();
            
            Flashcards = new ObservableCollection<Flashcard>(_database.GetAllFlashcards());
            DueFlashcards = new ObservableCollection<Flashcard>(_database.GetDueFlashcards());
            Notes = new ObservableCollection<Note>(_database.GetAllNotes());
            
            // Update statistics
            Statistics.CardsDueToday = DueFlashcards.Count;
            _database.SaveStatistics(Statistics);
            
            // Setup Pomodoro events
            _pomodoro.TimeUpdated += (s, time) =>
            {
                PomodoroTimeDisplay = $"{time.Minutes:D2}:{time.Seconds:D2}";
            };
            
            _pomodoro.StateChanged += (s, state) =>
            {
                PomodoroStateDisplay = state.ToString();
            };
            
            _pomodoro.IntervalCompleted += async (s, e) =>
            {
                // Show notification
                MessageBox.Show($"Pomodoro interval completed! Time for a {_pomodoro.CurrentState}", 
                    "StudyForge", MessageBoxButton.OK, MessageBoxImage.Information);
            };
            
            // Initialize commands
            NavigateToDashboardCommand = new RelayCommand(() => CurrentView = "Dashboard");
            NavigateToFlashcardsCommand = new RelayCommand(() => CurrentView = "Flashcards");
            NavigateToNotesCommand = new RelayCommand(() => CurrentView = "Notes");
            NavigateToPomodoroCommand = new RelayCommand(() => CurrentView = "Pomodoro");
            NavigateToSettingsCommand = new RelayCommand(() => CurrentView = "Settings");
            StartPomodoroCommand = new RelayCommand(() => _pomodoro.Start());
            PausePomodoroCommand = new RelayCommand(() => _pomodoro.Pause());
            ResetPomodoroCommand = new RelayCommand(() => _pomodoro.Reset());
            
            // Load API key if saved
            var apiKey = _database.GetSetting("ClaudeApiKey");
            if (!string.IsNullOrEmpty(apiKey))
            {
                _claudeApi.SetApiKey(apiKey);
            }
        }
        
        public DatabaseService GetDatabaseService() => _database;
        public ClaudeApiService GetClaudeApiService() => _claudeApi;
        public PomodoroService GetPomodoroService() => _pomodoro;
        
        public void RefreshData()
        {
            Flashcards.Clear();
            foreach (var card in _database.GetAllFlashcards())
                Flashcards.Add(card);
            
            DueFlashcards.Clear();
            foreach (var card in _database.GetDueFlashcards())
                DueFlashcards.Add(card);
            
            Notes.Clear();
            foreach (var note in _database.GetAllNotes())
                Notes.Add(note);
            
            Statistics = _database.GetStatistics();
            Statistics.CardsDueToday = DueFlashcards.Count;
        }
    }
    
    /// <summary>
    /// Simple relay command implementation
    /// </summary>
    public class RelayCommand : ICommand
    {
        private readonly Action _execute;
        private readonly Func<bool>? _canExecute;
        
        public RelayCommand(Action execute, Func<bool>? canExecute = null)
        {
            _execute = execute ?? throw new ArgumentNullException(nameof(execute));
            _canExecute = canExecute;
        }
        
        public event EventHandler? CanExecuteChanged
        {
            add => CommandManager.RequerySuggested += value;
            remove => CommandManager.RequerySuggested -= value;
        }
        
        public bool CanExecute(object? parameter) => _canExecute?.Invoke() ?? true;
        
        public void Execute(object? parameter) => _execute();
    }
}
