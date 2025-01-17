import { ApplicationConfig } from '@angular/core';
import { provideRouter } from '@angular/router';
import { AiAnalysisComponent } from './ai-analysis/ai-analysis.component';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter([
      { path: '', component: AiAnalysisComponent }, // Use as the default route
    ]),
  ],
};

