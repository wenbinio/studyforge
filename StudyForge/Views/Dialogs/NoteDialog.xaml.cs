using System.Windows;
using StudyForge.Models;

namespace StudyForge.Views.Dialogs
{
    public partial class NoteDialog : Window
    {
        public Note? Note { get; private set; }
        
        public NoteDialog(Note? existingNote = null)
        {
            InitializeComponent();
            
            if (existingNote != null)
            {
                Note = existingNote;
                TitleBox.Text = existingNote.Title;
                CategoryBox.Text = existingNote.Category;
                ContentBox.Text = existingNote.Content;
            }
            else
            {
                CategoryBox.Text = "General";
            }
        }
        
        private void Save_Click(object sender, RoutedEventArgs e)
        {
            if (string.IsNullOrWhiteSpace(TitleBox.Text) || string.IsNullOrWhiteSpace(ContentBox.Text))
            {
                MessageBox.Show("Title and Content are required.", "Validation Error", 
                    MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }
            
            if (Note == null)
            {
                Note = new Note();
            }
            
            Note.Title = TitleBox.Text.Trim();
            Note.Content = ContentBox.Text.Trim();
            Note.Category = string.IsNullOrWhiteSpace(CategoryBox.Text) ? "General" : CategoryBox.Text.Trim();
            
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
