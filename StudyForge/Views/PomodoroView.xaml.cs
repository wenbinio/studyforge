using System;
using System.Windows;
using System.Windows.Controls;
using StudyForge.ViewModels;

namespace StudyForge.Views
{
    public partial class PomodoroView : UserControl
    {
        public PomodoroView()
        {
            InitializeComponent();
        }
        
        private void ApplySettings_Click(object sender, RoutedEventArgs e)
        {
            if (DataContext is MainViewModel viewModel)
            {
                try
                {
                    int workMinutes = int.Parse(WorkDuration.Text);
                    int shortBreakMinutes = int.Parse(ShortBreak.Text);
                    int longBreakMinutes = int.Parse(LongBreak.Text);
                    
                    if (workMinutes <= 0 || shortBreakMinutes <= 0 || longBreakMinutes <= 0)
                    {
                        MessageBox.Show("All durations must be positive numbers.", "Invalid Input", 
                            MessageBoxButton.OK, MessageBoxImage.Warning);
                        return;
                    }
                    
                    var pomodoro = viewModel.GetPomodoroService();
                    pomodoro.Configure(workMinutes, shortBreakMinutes, longBreakMinutes, 4);
                    
                    MessageBox.Show("Settings applied successfully!", "StudyForge", 
                        MessageBoxButton.OK, MessageBoxImage.Information);
                }
                catch (FormatException)
                {
                    MessageBox.Show("Please enter valid numbers for all durations.", "Invalid Input", 
                        MessageBoxButton.OK, MessageBoxImage.Warning);
                }
            }
        }
    }
}
