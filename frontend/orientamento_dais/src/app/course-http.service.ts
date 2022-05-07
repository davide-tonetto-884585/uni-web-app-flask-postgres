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
export class CourseHttpService {

  constructor() { }
}
