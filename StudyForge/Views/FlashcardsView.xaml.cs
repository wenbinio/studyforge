using System.Windows;
using System.Windows.Controls;
using StudyForge.Models;
using StudyForge.ViewModels;
using StudyForge.Views.Dialogs;

namespace StudyForge.Views
{
    public partial class FlashcardsView : UserControl
    {
        public FlashcardsView()
        {
            InitializeComponent();
            Loaded += FlashcardsView_Loaded;
        }
        
        private void FlashcardsView_Loaded(object sender, RoutedEventArgs e)
        {
            if (DataContext is MainViewModel viewModel)
            {
                FlashcardList.ItemsSource = viewModel.Flashcards;
            }
        }
        
        private void CreateCard_Click(object sender, RoutedEventArgs e)
        {
            if (DataContext is MainViewModel viewModel)
            {
                var dialog = new FlashcardDialog();
                if (dialog.ShowDialog() == true && dialog.Flashcard != null)
                {
                    var db = viewModel.GetDatabaseService();
                    db.SaveFlashcard(dialog.Flashcard);
                    viewModel.RefreshData();
                    
                    // Update statistics
                    var stats = db.GetStatistics();
                    stats.CardsCreatedToday++;
                    db.SaveStatistics(stats);
                }
            }
        }
        
        private void EditCard_Click(object sender, RoutedEventArgs e)
        {
            if (sender is Button button && button.Tag is Flashcard card && DataContext is MainViewModel viewModel)
            {
                var dialog = new FlashcardDialog(card);
                if (dialog.ShowDialog() == true && dialog.Flashcard != null)
                {
                    var db = viewModel.GetDatabaseService();
                    db.SaveFlashcard(dialog.Flashcard);
                    viewModel.RefreshData();
                }
            }
        }
        
        private void DeleteCard_Click(object sender, RoutedEventArgs e)
        {
            if (sender is Button button && button.Tag is Flashcard card && DataContext is MainViewModel viewModel)
            {
                var result = MessageBox.Show($"Are you sure you want to delete this flashcard?\n\n{card.Question}", 
                    "Confirm Delete", MessageBoxButton.YesNo, MessageBoxImage.Question);
                
                if (result == MessageBoxResult.Yes)
                {
                    var db = viewModel.GetDatabaseService();
                    db.DeleteFlashcard(card.Id);
                    viewModel.RefreshData();
                }
            }
        }
        
        private void StartReview_Click(object sender, RoutedEventArgs e)
        {
            if (DataContext is MainViewModel viewModel)
            {
                var dueCards = viewModel.DueFlashcards;
                if (dueCards.Count == 0)
                {
                    MessageBox.Show("No cards are due for review!", "StudyForge", MessageBoxButton.OK, MessageBoxImage.Information);
                    return;
                }
                
                var reviewDialog = new ReviewSessionDialog(dueCards, viewModel.GetDatabaseService());
                reviewDialog.ShowDialog();
                viewModel.RefreshData();
            }
        }
    }
}
