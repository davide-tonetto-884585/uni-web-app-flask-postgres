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

  // ritorna i corsi aplicando eventuali filtri resi disponbili dal backend
  getCourses(limit = 10, skip = 0, title: string | null = null, lingua: string | null = null, scheduled: boolean | null = null, popular: boolean | null = null)
    : Observable<{ corsi: Course[], count: number }> {
    let params = {
      limit: limit,
      skip: skip,
      title: title,
      lingua: lingua,
      scheduled: scheduled,
      popular: popular
    }

    return this.http.get<{ corsi: Course[], count: number }>(
      `${BACKEND_URL}/corsi`,
      this.createOptions(Object.fromEntries(Object.entries(params).filter(([_, v]) => v != null)))
    ).pipe(catchError(this.handleError));
  }

  // reperisce un corso
  getCourse(id: number): Observable<Course> {
    return this.http.get<Course>(
      `${BACKEND_URL}/corsi/${id}`
    ).pipe(catchError(this.handleError));
  }

  // richiede i docenti assegnati ad un corso
  getDocentiCorso(id: number): Observable<any[]> {
    return this.http.get<any[]>(
      `${BACKEND_URL}/corsi/${id}/docenti`
    ).pipe(catchError(this.handleError));
  }

  // richiede gli iscritti ad una specifica programmazione del corso
  getIscrittiProgCorso(id_corso: number, id_prog_corso: number): Observable<any[]> {
    return this.http.get<any[]>(
      `${BACKEND_URL}/corsi/${id_corso}/programmazione_corso/${id_prog_corso}/iscrizioni`
    ).pipe(catchError(this.handleError));
  }

  // restituisce le lezioni di una programmazione di un corso
  getLezioniProgCorso(id_corso: number, id_prog_corso: number): Observable<Lesson[]> {
    return this.http.get<Lesson[]>(
      `${BACKEND_URL}/corsi/${id_corso}/programmazione_corso/${id_prog_corso}/lezioni`,
      this.createOptions()
    ).pipe(catchError(this.handleError));
  }

  // richiede le programmazioni di un corso con possibile filtro in_corso che permette di reperire solo i corsi con schedulazioni attive
  getProgrammazioniCorso(id_corso: number, in_corso: boolean | null = null): Observable<ProgCourse[]> {
    return this.http.get<ProgCourse[]>(
      `${BACKEND_URL}/corsi/${id_corso}/programmazione_corso`,
      this.createOptions(Object.fromEntries(Object.entries({ in_corso: in_corso }).filter(([_, v]) => v != null)))
    ).pipe(catchError(this.handleError));
  }

  // iscrive uno studente ad un programmazione di un corso
  enrollStudent(id_corso: number, id_prog_corso: number, id_stud: number, in_presenza: boolean | null = null): Observable<any> {
    const form_data = new FormData();
    form_data.append('id_studente', id_stud.toString())
    if (in_presenza !== null) form_data.append('in_presenza', in_presenza.toString())

    return this.http.post(
      `${BACKEND_URL}/corsi/${id_corso}/programmazione_corso/${id_prog_corso}/iscrizioni`,
      form_data,
      this.createOptions()
    ).pipe(catchError(this.handleError));
  }

  // restituisce i corsi appartenenti al docente indicato
  getCorsiDocente(id_docente: number): Observable<Course[]> {
    return this.http.get<Course[]>(
      `${BACKEND_URL}/utenti/docenti/${id_docente}/corsi`
    ).pipe(catchError(this.handleError));
  }

  // restituisce le iscrizioni di uno studente
  getInscriptionsStudent(id_studente: number): Observable<any> {
    return this.http.get(
      `${BACKEND_URL}/utenti/studenti/${id_studente}/iscrizioni`,
      this.createOptions()
    ).pipe(catchError(this.handleError));
  }

  // disiscrive uno studente dalla programmazione indicata
  unsubscribeStudent(id_corso: number, id_prog_corso: number, id_stud: number): Observable<any> {
    return this.http.delete(
      `${BACKEND_URL}/corsi/${id_corso}/programmazione_corso/${id_prog_corso}/iscrizioni/${id_stud}`,
      this.createOptions()
    ).pipe(catchError(this.handleError));
  }

  // aggiunge un nuovo corso
  addCourse(course: Course | any): Observable<any> {
    const form_data = new FormData();
    Object.keys(course).forEach((key) => {
      form_data.append(key, course[key]);
    });

    return this.http.post(BACKEND_URL + '/corsi', form_data, this.createOptions()).pipe(
      catchError(this.handleError)
    );
  }

  // aggiorna le informazioni di un corso
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

  // aggiunge docenti ad un corso
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

  // aggiunge una programmazione corso ad un corso
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

  // aggiorna le informazioni di una programmazione corso
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

  // aggiunge una lezione ad una programmazione corso
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

  // aggiorna le informazioni di una lezione corso
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

  // aggiunge una presenza al corso indicato per lo studente indicato
  addPresenzaCorso(id_corso: number, id_prog_corso: number, id_lezione: number, id_studente: number, passcode: string): Observable<any> {
    const form_data = new FormData();
    form_data.append('id_studente', id_studente.toString())
    form_data.append('codice_verifica_presenza', passcode)

    return this.http.post(
      `${BACKEND_URL}/corsi/${id_corso}/programmazione_corso/${id_prog_corso}/lezioni/${id_lezione}/presenze`,
      form_data,
      this.createOptions()
    ).pipe(catchError(this.handleError))
  }

  // invia la richiesta per il download del certificato di partecipazione
  getCertificate(id_corso: number, id_prog_corso: number): Observable<any> {
    return this.http.get(
      `${BACKEND_URL}/corsi/${id_corso}/programmazione_corso/${id_prog_corso}/certificato`,
      { observe: 'response', responseType: 'blob', ...this.createOptions() }
    ).pipe(catchError(() => {
      // se la prima richiesta va in errore ne eseguo un'altra per sapere il motivo dell'errore
      return this.http.get(
        `${BACKEND_URL}/corsi/${id_corso}/programmazione_corso/${id_prog_corso}/certificato`,
        this.createOptions()
      )
    }))
  }
}
