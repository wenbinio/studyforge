using System;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;
using System.Collections.Generic;

namespace StudyForge.Services
{
    /// <summary>
    /// Service for interacting with Claude API to generate study content
    /// </summary>
    public class ClaudeApiService
    {
        private readonly HttpClient _httpClient;
        private string _apiKey = string.Empty;
        private const string API_URL = "https://api.anthropic.com/v1/messages";
        
        public ClaudeApiService()
        {
            _httpClient = new HttpClient();
            _httpClient.DefaultRequestHeaders.Add("anthropic-version", "2023-06-01");
        }
        
        public void SetApiKey(string apiKey)
        {
            _apiKey = apiKey;
            if (_httpClient.DefaultRequestHeaders.Contains("x-api-key"))
                _httpClient.DefaultRequestHeaders.Remove("x-api-key");
            _httpClient.DefaultRequestHeaders.Add("x-api-key", apiKey);
        }
        
        /// <summary>
        /// Generate flashcards from lecture notes using Claude
        /// </summary>
        public async Task<List<(string question, string answer)>> GenerateFlashcardsFromNotes(string noteContent, int count = 5)
        {
            if (string.IsNullOrEmpty(_apiKey))
                throw new InvalidOperationException("API key not set. Please configure your Claude API key in settings.");
            
            var prompt = $@"Based on the following lecture notes, generate {count} high-quality flashcards for active recall study.
For each flashcard, provide a clear question and a concise answer.

Lecture Notes:
{noteContent}

Please format your response as a JSON array with objects containing 'question' and 'answer' fields.
Example format:
[
  {{""question"": ""What is...?"", ""answer"": ""...""}},
  {{""question"": ""How does...?"", ""answer"": ""...""}}
]";

            var response = await SendMessage(prompt);
            return ParseFlashcards(response);
        }
        
        /// <summary>
        /// Find an answer to a question from given material
        /// </summary>
        public async Task<string> FindAnswerInMaterial(string question, string material)
        {
            if (string.IsNullOrEmpty(_apiKey))
                throw new InvalidOperationException("API key not set. Please configure your Claude API key in settings.");
            
            var prompt = $@"Based on the following study material, answer this question:

Question: {question}

Study Material:
{material}

Please provide a clear, concise answer based solely on the information in the material. If the answer cannot be found in the material, say so.";

            return await SendMessage(prompt);
        }
        
        /// <summary>
        /// Generate a summary of study notes
        /// </summary>
        public async Task<string> SummarizeNotes(string noteContent)
        {
            if (string.IsNullOrEmpty(_apiKey))
                throw new InvalidOperationException("API key not set. Please configure your Claude API key in settings.");
            
            var prompt = $@"Please create a clear, concise summary of the following study notes, highlighting the key concepts and important points:

{noteContent}";

            return await SendMessage(prompt);
        }
        
        private async Task<string> SendMessage(string prompt)
        {
            var requestBody = new
            {
                model = "claude-3-5-sonnet-20241022",
                max_tokens = 2048,
                messages = new[]
                {
                    new { role = "user", content = prompt }
                }
            };
            
            var json = JsonConvert.SerializeObject(requestBody);
            var content = new StringContent(json, Encoding.UTF8, "application/json");
            
            try
            {
                var response = await _httpClient.PostAsync(API_URL, content);
                response.EnsureSuccessStatusCode();
                
                var responseJson = await response.Content.ReadAsStringAsync();
                var result = JsonConvert.DeserializeObject<ClaudeResponse>(responseJson);
                
                return result?.Content?[0]?.Text ?? "No response received";
            }
            catch (HttpRequestException ex)
            {
                throw new Exception($"Failed to communicate with Claude API: {ex.Message}", ex);
            }
        }
        
        private List<(string question, string answer)> ParseFlashcards(string response)
        {
            var flashcards = new List<(string question, string answer)>();
            
            try
            {
                // Try to extract JSON from the response
                var startIndex = response.IndexOf('[');
                var endIndex = response.LastIndexOf(']');
                
                if (startIndex >= 0 && endIndex > startIndex)
                {
                    var jsonArray = response.Substring(startIndex, endIndex - startIndex + 1);
                    var cards = JsonConvert.DeserializeObject<List<FlashcardData>>(jsonArray);
                    
                    if (cards != null)
                    {
                        foreach (var card in cards)
                        {
                            flashcards.Add((card.Question ?? "", card.Answer ?? ""));
                        }
                    }
                }
            }
            catch
            {
                // Fallback: create a single card with the response
                flashcards.Add(("Generated Content", response));
            }
            
            return flashcards;
        }
        
        private class ClaudeResponse
        {
            [JsonProperty("content")]
            public List<ContentBlock>? Content { get; set; }
        }
        
        private class ContentBlock
        {
            [JsonProperty("text")]
            public string? Text { get; set; }
        }
        
        private class FlashcardData
        {
            [JsonProperty("question")]
            public string? Question { get; set; }
            
            [JsonProperty("answer")]
            public string? Answer { get; set; }
        }
    }
}
