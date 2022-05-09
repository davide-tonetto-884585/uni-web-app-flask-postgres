import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams, HttpErrorResponse } from '@angular/common/http';
import { tap, catchError } from 'rxjs/operators';
import { Observable, throwError } from 'rxjs';
import jwt_decode from 'jwt-decode';

import { Course } from './models';
import { BACKEND_URL, FRONTEND_URL } from './globals';
import { UserHttpService } from './user-http.service';

@Injectable({
  providedIn: 'root'
})
export class CourseHttpService {

  constructor(
    private http: HttpClient,
    private user_http: UserHttpService
  ) { }

  private createOptions(params = {}) {
    return {
      headers: new HttpHeaders({
        authorization: 'Bearer ' + this.user_http.getToken(),
        'cache-control': 'no-cache',
        'Content-Type': 'application/json',
      }),
      params: new HttpParams({ fromObject: params })
    };
  }

  private handleError(error: HttpErrorResponse) {
    if (error.error instanceof ErrorEvent) {
      // A client-side or network error occurred. Handle it accordingly.
      console.error('An error occurred:', error.error.message);
    } else {
      // The backend returned an unsuccessful response code.
      // The response body may contain clues as to what went wrong,
      console.error(
        `Backend returned code ${error.status}, ` +
        'body was: ' + JSON.stringify(error.error));
    }

    return throwError(() => 'Something bad happened; please try again later.');
  }

  getCourses(limit = 10, skip = 0): Observable<Course[]> {
    return this.http.get<Course[]>(
      `${BACKEND_URL}/corsi`,
      this.createOptions({ limit: limit, skip: skip })
    ).pipe(catchError(this.handleError));
  }

}
