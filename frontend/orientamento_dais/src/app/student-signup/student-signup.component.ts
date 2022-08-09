import { Component, OnInit } from '@angular/core';

import { UserHttpService } from '../user-http.service';
import { Router } from '@angular/router';

import { User } from '../models'

@Component({
  selector: 'app-student-signup',
  templateUrl: './student-signup.component.html',
  styleUrls: ['./student-signup.component.css']
})
export class StudentSignupComponent implements OnInit {
  errmessage: string | undefined;
  user: User = { email: '', password: null, nome: '', cognome: '', data_nascita: '', sesso: '' };

  constructor(private user_http: UserHttpService, private router: Router) { }

  ngOnInit(): void {
  }

  signup(): void {
    this.user_http.registerStudent(this.user).subscribe({
      next: (d) => {
        console.log('Registration ok: ' + JSON.stringify(d));
        this.errmessage = undefined;
        this.router.navigate(['/login'], { queryParams: { errmessage: 'You will soon receive a confirmation email with an activation link to access the site' } });
      },
      error: (err) => {
        console.log('Signup error: ' + JSON.stringify(err.error.errormessage));
        this.errmessage = err.error.errormessage || err.error.message;
      }
    });
  }
}
