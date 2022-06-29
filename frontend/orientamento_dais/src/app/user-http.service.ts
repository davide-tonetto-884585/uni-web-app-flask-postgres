import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams, HttpErrorResponse } from '@angular/common/http';
import { tap, catchError } from 'rxjs/operators';
import { Observable, throwError } from 'rxjs';
import jwt_decode from 'jwt-decode';
import { Router } from '@angular/router';

import { User, UserData } from './models';
import { BACKEND_URL, FRONTEND_URL } from './globals';

@Injectable({
  providedIn: 'root'
})
export class UserHttpService {
  private token: string;
  private user_data: UserData | null;

  constructor(private http: HttpClient, private router: Router) {
    this.token = localStorage.getItem('token') ?? '';
    if (this.token.length < 1) {
      this.token = ""
      this.user_data = null;
    } else {
      this.user_data = jwt_decode<UserData>(this.token);
    }
  }

  private createOptions(params = {}) {
    return {
      headers: new HttpHeaders({
        'authorization': 'Bearer ' + this.getToken(),
        'cache-control': 'no-cache'
      }),
      params: new HttpParams({ fromObject: params })
    };
  }

  getToken(): string | null {
    if (this.user_data && Date.now() > +this.user_data?.exp * 1000) {
      this.logout();
      this.router.navigate(['/login']);
    }

    return this.token;
  }

  login(mail: string, password: string, remember: boolean): Observable<any> {
    const options = {
      headers: new HttpHeaders({
        "Authorization": "Basic " + btoa(mail + ":" + password),
        'cache-control': 'no-cache',
        'Content-Type': 'application/x-www-form-urlencoded',
      })
    };

    return this.http.get(BACKEND_URL + '/login', options).pipe(
      tap((data: any) => {
        this.token = data.token;
        this.user_data = jwt_decode<UserData>(this.token);
        if (remember) {
          localStorage.setItem('token', this.token);
        }
      }));
  }

  logout() {
    this.token = '';
    this.user_data = null;
    localStorage.setItem('token', this.token);
  }

  registerStudent(user: User | any): Observable<any> {
    const form_data = new FormData();
    Object.keys(user).forEach((key) => {
      form_data.append(key, user[key]);
    });

    form_data.append('frontend_activation_link', `${FRONTEND_URL}/activate`);

    return this.http.post(BACKEND_URL + '/utenti/studenti', form_data).pipe(
      tap((data: any) => {
        console.log(JSON.stringify(data));
      })
    );
  }

  completeRegistration(id: number, token: string, informations: any): Observable<any> {
    const form_data = new FormData();
    Object.keys(informations).forEach((key) => {
      form_data.append(key, informations[key]);
    });

    form_data.append('token_verifica', token);

    return this.http.post(BACKEND_URL + '/utenti/studenti/' + id, form_data).pipe(
      tap((data: any) => {
        console.log(JSON.stringify(data));
      })
    );
  }

  isLogged(): boolean {
    return (this.user_data && Date.now() <= +this.user_data?.exp * 1000) ? true : false;
  }

  isAdmin(): boolean {
    if (this.user_data) {
      return this.user_data.roles.includes('amministratore');
    }

    return false;
  }

  isStudent(): boolean {
    if (this.user_data) {
      return this.user_data.roles.includes('studente');
    }

    return false;
  }

  isTeacher(): boolean {
    if (this.user_data) {
      return this.user_data.roles.includes('docente');
    }

    return false;
  }

  getName(): string | boolean {
    return this.user_data?.nome ?? false;
  }

  getId(): number | undefined {
    return this.user_data?.id;
  }
}
