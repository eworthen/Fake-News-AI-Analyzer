import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common'; 
import { FormsModule } from '@angular/forms'; // Import FormsModule

@Component({
  selector: 'app-ai-analysis',
  standalone: true,
  imports: [CommonModule, FormsModule], // Add FormsModule here
  templateUrl: './ai-analysis.component.html',
  styleUrls: ['./ai-analysis.component.css']
})
export class AiAnalysisComponent {
  content: string = '';
  result: any = null;
  errorMessage: string | null = null;

  constructor(private http: HttpClient) {}

  submitForm() {
    const apiUrl = 'http://localhost:5000/analyze'; // Flask API URL
    this.http.post(apiUrl, { content: this.content }).subscribe({
      next: (response) => {
        this.result = response;
        this.errorMessage = null; // Clear any previous errors
      },
      error: (error) => {
        this.errorMessage = 'An error occurred while processing your request.';
        console.error('Error:', error);
      },
      complete: () => {
        console.log('AI analysis request completed.');
      }
    });
  }
}
