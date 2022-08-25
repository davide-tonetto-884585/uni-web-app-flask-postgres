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
export class AulaHttpService {
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

  // restituisce un'aula
  getAula(id_aula: number): Observable<Aula> {
    return this.http.get<Aula>(
      `${BACKEND_URL}/aule/${id_aula}`
    ).pipe(catchError(this.handleError));
  }

  // restituisce tutte le aule presenti nel database
  getAule(): Observable<Aula[]> {
    return this.http.get<Aula[]>(
      `${BACKEND_URL}/aule`
    ).pipe(catchError(this.handleError));
  }

  // aggiunge un'aula con le informazioni passate
  addAula(aula: Aula | any): Observable<any> {
    const form_data = new FormData();
    Object.keys(aula).forEach((key) => {
      form_data.append(key, aula[key]);
    });

    return this.http.post(
      `${BACKEND_URL}/aule`,
      form_data, 
      this.createOptions()
    ).pipe(catchError(this.handleError));
  }
}
