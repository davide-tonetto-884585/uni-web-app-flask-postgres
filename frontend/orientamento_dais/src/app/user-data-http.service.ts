import { HttpClient, HttpErrorResponse, HttpHeaders, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, Observable, throwError } from 'rxjs';
import { BACKEND_URL } from './globals';
import { Student, Teacher, User } from './models';
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

  getUserData(user_id: number): Observable<User> {
    return this.http.get<User>(
      `${BACKEND_URL}/utenti/${user_id}`,
      this.createOptions()
    ).pipe(catchError(this.handleError));
  }

  getTeacherData(teacher_id: number): Observable<Teacher> {
    return this.http.get<Teacher>(
      `${BACKEND_URL}/utenti/docenti/${teacher_id}`,
      this.createOptions()
    ).pipe(catchError(this.handleError));
  }

  getStudentData(student_id: number): Observable<Student> {
    return this.http.get<Student>(
      `${BACKEND_URL}/utenti/studenti/${student_id}`,
      this.createOptions()
    ).pipe(catchError(this.handleError));
  }

  updateStudentData(user: User | any, studentData: Student | any): Observable<any> {
    const form_data = new FormData();
    Object.keys(user).forEach((key) => {
      form_data.append(key, user[key]);
    });

    Object.keys(studentData).forEach((key) => {
      form_data.append(key, studentData[key]);
    });

    return this.http.put(
      `${BACKEND_URL}/utenti/studenti/${user.id}`,
      form_data, 
      this.createOptions()
    ).pipe(catchError(this.handleError));
  }

  updateTeacherData(user: User | any, teacherData: Teacher | any): Observable<any> {
    const form_data = new FormData();
    Object.keys(user).forEach((key) => {
      form_data.append(key, user[key]);
    });

    Object.keys(teacherData).forEach((key) => {
      form_data.append(key, teacherData[key]);
    });

    return this.http.put(
      `${BACKEND_URL}/utenti/docenti/${user.id}`,
      form_data, 
      this.createOptions()
    ).pipe(catchError(this.handleError));
  }
}
