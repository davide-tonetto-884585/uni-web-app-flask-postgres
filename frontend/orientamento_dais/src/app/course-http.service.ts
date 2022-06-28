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
export class CourseHttpService {

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

  getCourses(limit = 10, skip = 0): Observable<Course[]> {
    return this.http.get<Course[]>(
      `${BACKEND_URL}/corsi`,
      this.createOptions({ limit: limit, skip: skip })
    ).pipe(catchError(this.handleError));
  }

  getCourse(id: number): Observable<Course> {
    return this.http.get<Course>(
      `${BACKEND_URL}/corsi/${id}`
    ).pipe(catchError(this.handleError));
  }

  getDocentiCorso(id: number): Observable<any[]> {
    return this.http.get<any[]>(
      `${BACKEND_URL}/corsi/${id}/docenti`
    ).pipe(catchError(this.handleError));
  }

  getIscrittiProgCorso(id_corso: number, id_prog_corso: number): Observable<any[]> {
    return this.http.get<any[]>(
      `${BACKEND_URL}/corsi/${id_corso}/programmazione_corso/${id_prog_corso}/iscrizioni`
    ).pipe(catchError(this.handleError));
  }

  getLezioniProgCorso(id_corso: number, id_prog_corso: number): Observable<Lesson[]> {
    return this.http.get<Lesson[]>(
      `${BACKEND_URL}/corsi/${id_corso}/programmazione_corso/${id_prog_corso}/lezioni`,
      this.createOptions()
    ).pipe(catchError(this.handleError));
  }

  getProgrammazioniCorso(id: number): Observable<ProgCourse[]> {
    return this.http.get<ProgCourse[]>(
      `${BACKEND_URL}/corsi/${id}/programmazione_corso`
    ).pipe(catchError(this.handleError));
  }

  getAula(id_aula: number): Observable<Aula> {
    return this.http.get<Aula>(
      `${BACKEND_URL}/aule/${id_aula}`
    ).pipe(catchError(this.handleError));
  }

  enrollStudent(id_corso: number, id_prog_corso: number, id_stud: number): Observable<any> {
    const form_data = new FormData();
    form_data.append('id_studente', id_stud.toString())

    return this.http.post(
      `${BACKEND_URL}/corsi/${id_corso}/programmazione_corso/${id_prog_corso}/iscrizioni`,
      form_data,
      this.createOptions()
    ).pipe(catchError(this.handleError));
  }
}
