using System;
using System.IO;
using System.Windows;
using System.Windows.Controls;
using StudyForge.ViewModels;

namespace StudyForge.Views
{
    public partial class SettingsView : UserControl
    {
        public SettingsView()
        {
            InitializeComponent();
            Loaded += SettingsView_Loaded;
        }
        
        private void SettingsView_Loaded(object sender, RoutedEventArgs e)
        {
            // Set database path
            var appDataPath = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
                "StudyForge");
            var dbPath = Path.Combine(appDataPath, "studyforge.db");
            DatabasePath.Text = dbPath;
            
            // Load saved API key
            if (DataContext is MainViewModel viewModel)
            {
                var savedKey = viewModel.GetDatabaseService().GetSetting("ClaudeApiKey");
                if (!string.IsNullOrEmpty(savedKey))
                {
                    // Note: PasswordBox doesn't support binding, so we'd need to set it programmatically
                    // For security, we just show that a key is set
                }
            }
        }
        
        private void SaveApiKey_Click(object sender, RoutedEventArgs e)
        {
            if (DataContext is MainViewModel viewModel)
            {
                var apiKey = ApiKeyBox.Password;
                
                if (string.IsNullOrWhiteSpace(apiKey))
                {
                    MessageBox.Show("Please enter a valid API key.", "Invalid Input", 
                        MessageBoxButton.OK, MessageBoxImage.Warning);
                    return;
                }
                
                try
                {
                    var db = viewModel.GetDatabaseService();
                    db.SaveSetting("ClaudeApiKey", apiKey);
                    
                    var claudeApi = viewModel.GetClaudeApiService();
                    claudeApi.SetApiKey(apiKey);
                    
                    MessageBox.Show("API key saved successfully! AI features are now enabled.", "Success", 
                        MessageBoxButton.OK, MessageBoxImage.Information);
                    
                    ApiKeyBox.Clear();
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Error saving API key: {ex.Message}", "Error", 
                        MessageBoxButton.OK, MessageBoxImage.Error);
                }
            }
        }
        
        private void ResetStats_Click(object sender, RoutedEventArgs e)
        {
            var result = MessageBox.Show(
                "Are you sure you want to reset all statistics? This cannot be undone.", 
                "Confirm Reset", 
                MessageBoxButton.YesNo, 
                MessageBoxImage.Warning);
            
            if (result == MessageBoxResult.Yes)
            {
                if (DataContext is MainViewModel viewModel)
                {
                    var db = viewModel.GetDatabaseService();
                    var stats = new Models.StudyStatistics();
                    db.SaveStatistics(stats);
                    viewModel.RefreshData();
                    
                    MessageBox.Show("Statistics have been reset.", "Success", 
                        MessageBoxButton.OK, MessageBoxImage.Information);
                }
            }
        }
    }
}
