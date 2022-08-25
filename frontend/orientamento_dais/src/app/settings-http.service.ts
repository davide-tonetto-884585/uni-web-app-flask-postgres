import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams, HttpErrorResponse } from '@angular/common/http';
import { tap, catchError } from 'rxjs/operators';
import { Observable, throwError } from 'rxjs';

import { Course, Lesson, ProgCourse, Aula } from './models';
import { BACKEND_URL, FRONTEND_URL } from './globals';
import { UserHttpService } from './user-http.service';

@Injectable({
  providedIn: 'root'
})
export class SettingsHttpService {

  constructor(
    private http: HttpClient,
    private user_http: UserHttpService,
  ) { }

  private createOptions(params = {}) {
    return {
      headers: new HttpHeaders({
        'authorization': 'Bearer ' + this.user_http.getToken(),
        'cache-control': 'no-cache'
      }),
      params: new HttpParams({ fromObject: params })
    };
  }

  private handleError(error: HttpErrorResponse) {
    if (error.error instanceof ErrorEvent) {
      console.error('An error occurred:', error.error.message);
      return throwError(() => error.error.message);
    } else {
      console.error(
        `Backend returned code ${error.status}, ` +
        'body was: ' + JSON.stringify(error.error));

      return throwError(() => error.error.errormessage);
    }
  }

  // richiede le attuali impostazioni globali dell'applicativo
  getCurrentSettings(): Observable<any> {
    return this.http.get<any>(
      `${BACKEND_URL}/impostazioni`,
      this.createOptions()
    ).pipe(catchError(this.handleError))
  }

  // aggiorna le impostazioni globali del'applicativo
  updateSettings(settings: any): Observable<any> {
    const form_data = new FormData();
    Object.keys(settings).forEach((key) => {
      form_data.append(key, settings[key]);
    });

    return this.http.put<any>(
      `${BACKEND_URL}/impostazioni`,
      form_data,
      this.createOptions()
    ).pipe(catchError(this.handleError))
  }
}