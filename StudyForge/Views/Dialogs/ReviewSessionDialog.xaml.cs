using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Windows;
using StudyForge.Models;
using StudyForge.Services;

namespace StudyForge.Views.Dialogs
{
    public partial class ReviewSessionDialog : Window
    {
        private readonly ObservableCollection<Flashcard> _cards;
        private readonly DatabaseService _database;
        private int _currentIndex = 0;
        private int _reviewedCount = 0;
        
        public ReviewSessionDialog(ObservableCollection<Flashcard> cards, DatabaseService database)
        {
            InitializeComponent();
            _cards = cards;
            _database = database;
            
            if (_cards.Count > 0)
            {
                ShowCurrentCard();
            }
            else
            {
                MessageBox.Show("No cards to review!", "StudyForge", 
                    MessageBoxButton.OK, MessageBoxImage.Information);
                Close();
            }
        }
        
        private void ShowCurrentCard()
        {
            if (_currentIndex >= _cards.Count)
            {
                ShowCompletionMessage();
                return;
            }
            
            var card = _cards[_currentIndex];
            QuestionText.Text = card.Question;
            QuestionText2.Text = card.Question;
            AnswerText.Text = card.Answer;
            
            ProgressText.Text = $"Card {_currentIndex + 1} of {_cards.Count}";
            ProgressBar.Maximum = _cards.Count;
            ProgressBar.Value = _currentIndex;
            
            // Reset visibility
            QuestionPanel.Visibility = Visibility.Visible;
            AnswerPanel.Visibility = Visibility.Collapsed;
            RatingPanel.Visibility = Visibility.Collapsed;
        }
        
        private void ShowAnswer_Click(object sender, RoutedEventArgs e)
        {
            QuestionPanel.Visibility = Visibility.Collapsed;
            AnswerPanel.Visibility = Visibility.Visible;
            RatingPanel.Visibility = Visibility.Visible;
        }
        
        private void Rate_Click(object sender, RoutedEventArgs e)
        {
            if (sender is not System.Windows.Controls.Button button || button.Tag is not string tagStr)
                return;
            
            int quality = int.Parse(tagStr);
            var card = _cards[_currentIndex];
            
            // Update card schedule using SM-2 algorithm
            card.UpdateSchedule(quality);
            _database.SaveFlashcard(card);
            
            _reviewedCount++;
            _currentIndex++;
            
            // Update statistics
            var stats = _database.GetStatistics();
            stats.TotalCardsReviewed++;
            stats.UpdateStreak();
            _database.SaveStatistics(stats);
            
            ShowCurrentCard();
        }
        
        private void EndSession_Click(object sender, RoutedEventArgs e)
        {
            if (_reviewedCount > 0)
            {
                var result = MessageBox.Show(
                    $"You've reviewed {_reviewedCount} card(s). Are you sure you want to end this session?",
                    "End Session",
                    MessageBoxButton.YesNo,
                    MessageBoxImage.Question);
                
                if (result == MessageBoxResult.Yes)
                {
                    Close();
                }
            }
            else
            {
                Close();
            }
        }
        
        private void ShowCompletionMessage()
        {
            MessageBox.Show(
                $"Congratulations! You've completed the review session.\n\nCards reviewed: {_reviewedCount}",
                "Session Complete",
                MessageBoxButton.OK,
                MessageBoxImage.Information);
            Close();
        }
    }
}
