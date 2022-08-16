import { HttpClient, HttpErrorResponse, HttpHeaders, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, Observable, throwError } from 'rxjs';
import { BACKEND_URL } from './globals';
import { UserHttpService } from './user-http.service';

@Injectable({
  providedIn: 'root'
})
export class UserDataHttpService {

  constructor(private http: HttpClient, private user_http: UserHttpService) { }

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

  getUserData(user_id: number): Observable<any> {
    return this.http.get(
      `${BACKEND_URL}/utenti/${user_id}`,
      this.createOptions()
    ).pipe(catchError(this.handleError));
  }

  getTeacherData(teacher_id: number): Observable<any> {
    return this.http.get(
      `${BACKEND_URL}/utenti/docenti/${teacher_id}`,
      this.createOptions()
    ).pipe(catchError(this.handleError));
  }
}
