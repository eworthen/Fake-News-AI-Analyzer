import { Component } from '@angular/core';
import { AiAnalysisComponent } from './ai-analysis/ai-analysis.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [AiAnalysisComponent],
  template: '<app-ai-analysis></app-ai-analysis>', // Use the selector here
  styleUrls: ['./app.component.css'] // Correct usage of `styleUrls`
})
export class AppComponent {
  title = 'angular';
}

