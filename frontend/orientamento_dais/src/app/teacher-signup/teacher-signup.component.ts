import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { User } from '../models';
import { UserHttpService } from '../user-http.service';

@Component({
  selector: 'app-teacher-signup',
  templateUrl: './teacher-signup.component.html',
  styleUrls: ['./teacher-signup.component.css']
})
export class TeacherSignupComponent implements OnInit {
  errmessage: string | undefined;
  user: User = { email: '', password: null, nome: '', cognome: '', data_nascita: '', sesso: '' };

  constructor(
    private user_http: UserHttpService,
    private router: Router
  ) { }

  ngOnInit(): void {
    if (!this.user_http.isAdmin())
      this.router.navigate(['/home']);
  }

  signup(): void {
    this.user_http.registerTeacher(this.user).subscribe({
      next: (d) => {
        console.log('Registration ok: ' + JSON.stringify(d));
        this.errmessage = undefined;
        this.router.navigate(['/home'], { queryParams: { error: false, message: 'The teacher will receive a confirmation email containing a link for activating the profile' } });
      },
      error: (err) => {
        console.log('Signup error: ' + JSON.stringify(err.error.errormessage));
        this.errmessage = err.error.errormessage || err.error.message;
      }
    });
  }
}
