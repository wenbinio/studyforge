using System.Windows;
using StudyForge.Models;

namespace StudyForge.Views.Dialogs
{
    public partial class FlashcardDialog : Window
    {
        public Flashcard? Flashcard { get; private set; }
        
        public FlashcardDialog(Flashcard? existingCard = null)
        {
            InitializeComponent();
            
            if (existingCard != null)
            {
                Flashcard = existingCard;
                CategoryBox.Text = existingCard.Category;
                QuestionBox.Text = existingCard.Question;
                AnswerBox.Text = existingCard.Answer;
                NotesBox.Text = existingCard.Notes ?? "";
            }
            else
            {
                CategoryBox.Text = "General";
            }
        }
        
        private void Save_Click(object sender, RoutedEventArgs e)
        {
            if (string.IsNullOrWhiteSpace(QuestionBox.Text) || string.IsNullOrWhiteSpace(AnswerBox.Text))
            {
                MessageBox.Show("Question and Answer are required.", "Validation Error", 
                    MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }
            
            if (Flashcard == null)
            {
                Flashcard = new Flashcard();
            }
            
            Flashcard.Question = QuestionBox.Text.Trim();
            Flashcard.Answer = AnswerBox.Text.Trim();
            Flashcard.Category = string.IsNullOrWhiteSpace(CategoryBox.Text) ? "General" : CategoryBox.Text.Trim();
            Flashcard.Notes = string.IsNullOrWhiteSpace(NotesBox.Text) ? null : NotesBox.Text.Trim();
            
            DialogResult = true;
            Close();
        }
        
        private void Cancel_Click(object sender, RoutedEventArgs e)
        {
            DialogResult = false;
            Close();
        }
    }
}
