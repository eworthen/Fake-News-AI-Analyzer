import { bootstrapApplication } from '@angular/platform-browser';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { appConfig } from './app/app.config';
import { AppComponent } from './app/app.component';

// Define custom interceptors if needed (optional)
const customInterceptors = withInterceptors([]); // Add your functional interceptors here if required.

bootstrapApplication(AppComponent, {
  ...appConfig,
  providers: [
    ...(appConfig.providers || []), // Spread existing providers from appConfig
    provideHttpClient(customInterceptors), // Add HttpClient configuration
  ]
}).catch((err) => console.error(err));
