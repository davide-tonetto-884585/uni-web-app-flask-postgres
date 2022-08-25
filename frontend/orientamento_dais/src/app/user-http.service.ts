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
  // token usato per autenticazione
  private token: string;
  // dati dell'utente loggato
  private user_data: UserData | null;

  constructor(private http: HttpClient, private router: Router) {
    // controllo se vi è gia un token salvato dal browser, se si l'utente è gia loggato
    this.token = localStorage.getItem('token') ?? '';
    if (this.token.length < 1) {
      this.token = ""
      this.user_data = null;
    } else {
      this.user_data = jwt_decode<UserData>(this.token);
    }
  }

  // crea le opzioni di base per le richieste includendo il token di autenticazione
  private createOptions(params = {}) {
    return {
      headers: new HttpHeaders({
        'authorization': 'Bearer ' + this.getToken(),
        'cache-control': 'no-cache'
      }),
      params: new HttpParams({ fromObject: params })
    };
  }

  // restituisce il token di autenticazione
  getToken(): string | null {
    if (this.user_data && Date.now() > +this.user_data?.exp * 1000) {
      this.logout();
      this.router.navigate(['/login']);
    }

    return this.token;
  }

  // logga un utente se mail e password corrispondono
  login(mail: string, password: string, remember: boolean): Observable<any> {
    // creo opzioni richiesta HTTP
    const options = {
      headers: new HttpHeaders({
        "Authorization": "Basic " + btoa(mail + ":" + password),
        'cache-control': 'no-cache',
        'Content-Type': 'application/x-www-form-urlencoded',
      })
    };

    // invio richiesta login al backend 
    return this.http.get(BACKEND_URL + '/login', options).pipe(
      tap((data: any) => {
        this.token = data.token;
        // estrapolo dati dal token
        this.user_data = jwt_decode<UserData>(this.token);

        // se ha attivato la spunta remember allora salvo la sessione
        if (remember) {
          localStorage.setItem('token', this.token);
        }
      }));
  }

  // elimina dati utente loggato
  logout() {
    this.token = '';
    this.user_data = null;
    localStorage.setItem('token', this.token);
  }

  // registra un nuovo studente all'applicativo
  registerStudent(user: User | any): Observable<any> {
    // creo il body della richiesta
    const form_data = new FormData();
    Object.keys(user).forEach((key) => {
      form_data.append(key, user[key]);
    });

    form_data.append('frontend_activation_link', `${FRONTEND_URL}/activate`);

    // invio richiesta la backend
    return this.http.post(BACKEND_URL + '/utenti/studenti', form_data).pipe(
      tap((data: any) => {
        console.log(JSON.stringify(data));
      })
    );
  }

  // registrazione nuovo docente
  registerTeacher(user: User | any): Observable<any> {
    const form_data = new FormData();
    Object.keys(user).forEach((key) => {
      form_data.append(key, user[key]);
    });

    form_data.append('frontend_activation_link', `${FRONTEND_URL}/activate`);

    return this.http.post(BACKEND_URL + '/utenti/docenti', form_data, this.createOptions()).pipe(
      tap((data: any) => {
        console.log(JSON.stringify(data));
      })
    );
  }

  // completamento registrazione nuovo studente (conferma mail)
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

  // completamento registrazione nuovo docente (conferma mail)
  completeTeacherRegistration(id: number, token: string, informations: any): Observable<any> {
    const form_data = new FormData();
    Object.keys(informations).forEach((key) => {
      form_data.append(key, informations[key]);
    });

    form_data.append('token_verifica', token);

    return this.http.post(BACKEND_URL + '/utenti/docenti/' + id, form_data).pipe(
      tap((data: any) => {
        console.log(JSON.stringify(data));
      })
    );
  }

  // ritorna true se l'utente è loggato
  isLogged(): boolean {
    return (this.user_data && Date.now() <= +this.user_data?.exp * 1000) ? true : false;
  }

  // ritorna true se l'utente è un admin
  isAdmin(): boolean {
    if (this.user_data) {
      return this.user_data.roles.includes('amministratore');
    }

    return false;
  }

  // ritorna true se l'utente è uno studente
  isStudent(): boolean {
    if (this.user_data) {
      return this.user_data.roles.includes('studente');
    }

    return false;
  }

  // ritorna true se l'utente è un docente
  isTeacher(): boolean {
    if (this.user_data) {
      return this.user_data.roles.includes('docente');
    }

    return false;
  }

  // ritorna il nome dell'utente loggato se presente
  getName(): string | boolean {
    return this.user_data?.nome ?? false;
  }

  // ritorna l'ID dell'utente loggato se presente
  getId(): number | undefined {
    return this.user_data?.id;
  }
}
