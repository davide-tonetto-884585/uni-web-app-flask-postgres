import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams, HttpErrorResponse } from '@angular/common/http';
import { tap, catchError } from 'rxjs/operators';
import { Observable, throwError } from 'rxjs';
import * as jwtdecode from 'jwt-decode';

import { Router } from '@angular/router';
import { User } from './models';

@Injectable({
  providedIn: 'root'
})
export class UserHttpService {
  private token: string;
  public readonly BACKEND_URL = 'http://localhost:5000';
  public readonly FRONTEND_URL = 'http://localhost:4200';

  constructor(private http: HttpClient, private router: Router) {
    this.token = localStorage.getItem('token') ?? '';
    if (this.token.length < 1) {
      this.token = ""
    }
  }

  login(mail: string, password: string, remember: boolean): Observable<any> {
    const options = {
      headers: new HttpHeaders({
        "Authorization": "Basic " + btoa(mail + ":" + password),
        'cache-control': 'no-cache',
        'Content-Type': 'application/x-www-form-urlencoded',
      })
    };

    return this.http.get(this.BACKEND_URL + '/login', options).pipe(
      tap((data: any) => {
        console.log(JSON.stringify(data));
        this.token = data.token;
        if (remember) {
          localStorage.setItem('token', this.token);
        }
      }));
  }

  logout() {
    this.token = '';
    localStorage.setItem('token', this.token);
  }

  register_student(user: User | any): Observable<any> {
    const form_data = new FormData();
    Object.keys(user).forEach((key) => {
      form_data.append(key, user[key]);
    });

    form_data.append('frontend_activation_link', `${this.FRONTEND_URL}/activate`);

    return this.http.post(this.BACKEND_URL + '/studenti', form_data).pipe(
      tap((data: any) => {
        console.log(JSON.stringify(data));
      })
    );
  }

  complete_registration(id: number, token: string, informations: any): Observable<any> {
    const form_data = new FormData();
    Object.keys(informations).forEach((key) => {
      form_data.append(key, informations[key]);
    });

    form_data.append('token_verifica', token);

    return this.http.post(this.BACKEND_URL + '/studenti/' + id, form_data).pipe(
      tap((data: any) => {
        console.log(JSON.stringify(data));
      })
    );
  }

  get_token(): string {
    return this.token;
  }
}
