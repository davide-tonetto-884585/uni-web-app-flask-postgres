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

  getCourses(limit = 10, skip = 0, title: string | null = null, lingua: string | null = null, scheduled: boolean | null = null)
    : Observable<{ corsi: Course[], count: number }> {
    let params = {
      limit: limit,
      skip: skip,
      title: title,
      lingua: lingua,
      scheduled: scheduled
    }

    return this.http.get<{ corsi: Course[], count: number }>(
      `${BACKEND_URL}/corsi`,
      this.createOptions(Object.fromEntries(Object.entries(params).filter(([_, v]) => v != null)))
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

  getProgrammazioniCorso(id_corso: number, in_corso: boolean | null = null): Observable<ProgCourse[]> {
    return this.http.get<ProgCourse[]>(
      `${BACKEND_URL}/corsi/${id_corso}/programmazione_corso`,
      this.createOptions(Object.fromEntries(Object.entries({ in_corso: in_corso }).filter(([_, v]) => v != null)))
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

  getCorsiDocente(id_docente: number): Observable<Course[]> {
    return this.http.get<Course[]>(
      `${BACKEND_URL}/utenti/docenti/${id_docente}/corsi`
    ).pipe(catchError(this.handleError));
  }

  getInscriptionsStudent(id_studente: number): Observable<any> {
    return this.http.get(
      `${BACKEND_URL}/utenti/studenti/${id_studente}/iscrizioni`,
      this.createOptions()
    ).pipe(catchError(this.handleError));
  }

  unsubscribeStudent(id_corso: number, id_prog_corso: number, id_stud: number): Observable<any> {
    return this.http.delete(
      `${BACKEND_URL}/corsi/${id_corso}/programmazione_corso/${id_prog_corso}/iscrizioni/${id_stud}`,
      this.createOptions()
    ).pipe(catchError(this.handleError));
  }

  addCourse(course: Course | any): Observable<any> {
    const form_data = new FormData();
    Object.keys(course).forEach((key) => {
      form_data.append(key, course[key]);
    });

    return this.http.post(BACKEND_URL + '/corsi', form_data, this.createOptions()).pipe(
      catchError(this.handleError)
    );
  }

  updateCourse(course: Course | any): Observable<any> {
    const form_data = new FormData();
    Object.keys(course).forEach((key) => {
      if (course[key] != null)
        form_data.append(key, course[key]);
    });

    return this.http.put(BACKEND_URL + '/corsi/' + course.id, form_data, this.createOptions()).pipe(
      catchError(this.handleError)
    );
  }

  addDocentiCorso(id_corso: number, id_docenti: number[]): Observable<any> {
    const form_data = new FormData();

    id_docenti.forEach((id) => {
      form_data.append('id_docenti[]', id.toString());
    })

    return this.http.post(
      `${BACKEND_URL}/corsi/${id_corso}/docenti`,
      form_data,
      this.createOptions()
    ).pipe(catchError(this.handleError))
  }

  addProgCorso(id_corso: number, prog_corso: ProgCourse | any): Observable<any> {
    const form_data = new FormData();
    Object.keys(prog_corso).forEach((key) => {
      form_data.append(key, prog_corso[key]);
    });

    return this.http.post(
      `${BACKEND_URL}/corsi/${id_corso}/programmazione_corso`,
      form_data,
      this.createOptions()
    ).pipe(catchError(this.handleError));
  }

  updateProgCorso(id_corso: number, prog_corso: ProgCourse | any): Observable<any> {
    const form_data = new FormData();
    Object.keys(prog_corso).forEach((key) => {
      form_data.append(key, prog_corso[key]);
    });

    return this.http.put(
      `${BACKEND_URL}/corsi/${id_corso}/programmazione_corso/${prog_corso.id}`,
      form_data,
      this.createOptions()
    ).pipe(catchError(this.handleError));
  }

  addLezioneProg(id_corso: number, id_prog_corso: number, lezione: Lesson | any): Observable<any> {
    const form_data = new FormData();
    Object.keys(lezione).forEach((key) => {
      form_data.append(key, lezione[key]);
    });

    return this.http.post(
      `${BACKEND_URL}/corsi/${id_corso}/programmazione_corso/${id_prog_corso}/lezioni`,
      form_data,
      this.createOptions()
    ).pipe(catchError(this.handleError));
  }

  updateLezioneProg(id_corso: number, id_prog_corso: number, lezione: Lesson | any): Observable<any> {
    const form_data = new FormData();
    Object.keys(lezione).forEach((key) => {
      form_data.append(key, lezione[key]);
    });

    return this.http.put(
      `${BACKEND_URL}/corsi/${id_corso}/programmazione_corso/${id_prog_corso}/lezioni/${lezione.id}`,
      form_data,
      this.createOptions()
    ).pipe(catchError(this.handleError));
  }

  addPresenzaCorso(id_corso: number, id_prog_corso: number, id_lezione: number, id_studente: number, passcode: string): Observable<any> {
    const form_data = new FormData();
    form_data.append('id_studente', id_studente.toString())
    form_data.append('codice_verifica_presenza', passcode)

    return this.http.post(
      `${BACKEND_URL}/corsi/${id_corso}/programmazione_corso/${id_prog_corso}/lezioni/${id_lezione}/presenze`,
      form_data,
      this.createOptions()
    )
  }
}
