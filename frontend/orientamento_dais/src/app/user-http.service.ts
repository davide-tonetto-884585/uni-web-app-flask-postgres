import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams, HttpErrorResponse } from '@angular/common/http';
import { tap, catchError } from 'rxjs/operators';
import { Observable, throwError } from 'rxjs';
import * as jwtdecode from 'jwt-decode';

@Injectable({
  providedIn: 'root'
})
export class UserHttpService {
  private token: string;
  public readonly BACKEND_URL = 'http://localhost:5000';

  constructor(private http: HttpClient) {
    this.token = localStorage.getItem('token') ?? '';
    if (this.token.length < 1) {
      this.token = ""
    }
  }

  login(mail: string, password: string, remember: boolean): Observable<any> {
    const options = {
      headers: new HttpHeaders({
        authorization: 'Basic ' + btoa(mail + ':' + password),
        'cache-control': 'no-cache',
        'Content-Type': 'application/x-www-form-urlencoded',
      })
    };

    return this.http.get(this.BACKEND_URL + '/login', options,).pipe(
      tap((data) => {
        this.token = data.token;
        if (remember) {
          localStorage.setItem('token', this.token);
        }
      }));
  }
}
