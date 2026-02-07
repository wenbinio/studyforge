using System;
using System.Linq;
using System.Windows;
using System.Windows.Controls;
using StudyForge.Models;
using StudyForge.ViewModels;
using StudyForge.Views.Dialogs;

namespace StudyForge.Views
{
    public partial class NotesView : UserControl
    {
        public NotesView()
        {
            InitializeComponent();
            Loaded += NotesView_Loaded;
        }
        
        private void NotesView_Loaded(object sender, RoutedEventArgs e)
        {
            if (DataContext is MainViewModel viewModel)
            {
                NotesList.ItemsSource = viewModel.Notes;
            }
        }
        
        private void CreateNote_Click(object sender, RoutedEventArgs e)
        {
            if (DataContext is MainViewModel viewModel)
            {
                var dialog = new NoteDialog();
                if (dialog.ShowDialog() == true && dialog.Note != null)
                {
                    var db = viewModel.GetDatabaseService();
                    db.SaveNote(dialog.Note);
                    viewModel.RefreshData();
                }
            }
        }
        
        private void EditNote_Click(object sender, RoutedEventArgs e)
        {
            if (sender is Button button && button.Tag is Note note && DataContext is MainViewModel viewModel)
            {
                var dialog = new NoteDialog(note);
                if (dialog.ShowDialog() == true && dialog.Note != null)
                {
                    var db = viewModel.GetDatabaseService();
                    db.SaveNote(dialog.Note);
                    viewModel.RefreshData();
                }
            }
        }
        
        private void DeleteNote_Click(object sender, RoutedEventArgs e)
        {
            if (sender is Button button && button.Tag is Note note && DataContext is MainViewModel viewModel)
            {
                var result = MessageBox.Show($"Are you sure you want to delete this note?\n\n{note.Title}", 
                    "Confirm Delete", MessageBoxButton.YesNo, MessageBoxImage.Question);
                
                if (result == MessageBoxResult.Yes)
                {
                    var db = viewModel.GetDatabaseService();
                    db.DeleteNote(note.Id);
                    viewModel.RefreshData();
                }
            }
        }
        
        private async void GenerateCards_Click(object sender, RoutedEventArgs e)
        {
            if (DataContext is MainViewModel viewModel)
            {
                var selectedNote = NotesList.SelectedItem as Note;
                if (selectedNote == null)
                {
                    MessageBox.Show("Please select a note to generate flashcards from.", "No Note Selected", 
                        MessageBoxButton.OK, MessageBoxImage.Information);
                    return;
                }
                
                try
                {
                    var claudeApi = viewModel.GetClaudeApiService();
                    var db = viewModel.GetDatabaseService();
                    
                    // Show loading message
                    var loadingWindow = new Window
                    {
                        Title = "Generating Flashcards",
                        Content = new TextBlock 
                        { 
                            Text = "Using Claude AI to generate flashcards from your notes...\nThis may take a moment.",
                            Padding = new Thickness(40),
                            FontSize = 14,
                            TextAlignment = TextAlignment.Center
                        },
                        Width = 400,
                        Height = 150,
                        WindowStartupLocation = WindowStartupLocation.CenterOwner,
                        Owner = Window.GetWindow(this),
                        ResizeMode = ResizeMode.NoResize
                    };
                    loadingWindow.Show();
                    
                    var flashcards = await claudeApi.GenerateFlashcardsFromNotes(selectedNote.Content, 5);
                    
                    loadingWindow.Close();
                    
                    if (flashcards.Count > 0)
                    {
                        foreach (var (question, answer) in flashcards)
                        {
                            var card = new Flashcard
                            {
                                Question = question,
                                Answer = answer,
                                Category = selectedNote.Category,
                                GeneratedByAI = true,
                                SourceMaterial = selectedNote.Title
                            };
                            db.SaveFlashcard(card);
                            selectedNote.GeneratedFlashcardIds.Add(card.Id);
                        }
                        
                        db.SaveNote(selectedNote);
                        viewModel.RefreshData();
                        
                        MessageBox.Show($"Successfully generated {flashcards.Count} flashcards from your notes!", 
                            "Success", MessageBoxButton.OK, MessageBoxImage.Information);
                    }
                    else
                    {
                        MessageBox.Show("Could not generate flashcards. Please check your API key and try again.", 
                            "Error", MessageBoxButton.OK, MessageBoxImage.Warning);
                    }
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Error generating flashcards: {ex.Message}", "Error", 
                        MessageBoxButton.OK, MessageBoxImage.Error);
                }
            }
        }
    }
}
