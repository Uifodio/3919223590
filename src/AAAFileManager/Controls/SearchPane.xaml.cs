using System;
using System.Threading;
using System.Windows;
using System.Windows.Controls;

namespace AAAFileManager
{
    public partial class SearchPane : UserControl
    {
        private CancellationTokenSource? _cts;

        public event EventHandler<SearchRequestedEventArgs>? SearchRequested;

        public SearchPane()
        {
            InitializeComponent();
        }

        private void Search_Click(object sender, RoutedEventArgs e)
        {
            _cts?.Cancel();
            _cts = new CancellationTokenSource();
            SearchRequested?.Invoke(this, new SearchRequestedEventArgs
            {
                NameQuery = NameQuery.Text,
                ContentQuery = ContentQuery.Text,
                CancellationToken = _cts.Token
            });
        }

        private void Cancel_Click(object sender, RoutedEventArgs e)
        {
            _cts?.Cancel();
        }
    }

    public class SearchRequestedEventArgs : EventArgs
    {
        public string? NameQuery { get; set; }
        public string? ContentQuery { get; set; }
        public CancellationToken CancellationToken { get; set; }
    }
}