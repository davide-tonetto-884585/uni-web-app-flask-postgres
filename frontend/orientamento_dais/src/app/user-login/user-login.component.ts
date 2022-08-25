import { Component, OnInit } from '@angular/core';

import { UserHttpService } from '../user-http.service';
import { Router, ActivatedRoute } from '@angular/router';
import { CourseHttpService } from '../course-http.service';

import * as CryptoJS from 'crypto-js';
import { SECRET } from '../globals';

@Component({
  selector: 'app-user-login',
  templateUrl: './user-login.component.html',
  styleUrls: ['./user-login.component.css']
})
export class UserLoginComponent implements OnInit {
  errmessage: string | undefined;
  pres_code: string | undefined;

  constructor(
    private user_http: UserHttpService,
    private course_http: CourseHttpService,
    private router: Router,
    private activated_rouer: ActivatedRoute
  ) { }

  ngOnInit(): void {
    this.activated_rouer.queryParams.subscribe(params => {
      this.pres_code = params['pres_code'];
      if (params['errmessage']) this.errmessage = params['errmessage'];
    });

    if (this.user_http.isLogged()) {
      if (this.pres_code != undefined) {
        let id_studente = this.user_http.getId();
        if (id_studente != undefined)
          this.addAttendance(id_studente)
      } else {
        this.router.navigate(['/home']);
      }
    }
  }

  addAttendance(id_studente: number): void {
    if (this.pres_code != undefined) {
      let dot_index = this.pres_code.indexOf('.');
      let id_corso = this.pres_code.substring(0, dot_index);
      let id_prog_corso = this.pres_code.substring(dot_index + 1, this.pres_code.indexOf('.', dot_index + 1));
      dot_index = this.pres_code.indexOf('.', dot_index + 1)
      let id_lezione = this.pres_code.substring(dot_index + 1, this.pres_code.indexOf('.', dot_index + 1));
      let passcode = CryptoJS.AES.decrypt(
        this.pres_code.substring(this.pres_code.indexOf('.', dot_index + 1) + 1),
        SECRET
      ).toString(CryptoJS.enc.Utf8);

      this.course_http.addPresenzaCorso(+id_corso, +id_prog_corso, +id_lezione, +id_studente, passcode).subscribe({
        next: (d) => {
          this.router.navigate(['/home'], { queryParams: { error: false, message: 'Attendance registered successfully' } })
        },
        error: (err) => {
          this.router.navigate(['/home'], { queryParams: { error: true, message: 'Attendance registered failed: ' + err } })
        }
      })
    }
  }

  login(mail: string, password: string, remember: boolean) {
    this.user_http.login(mail, password, remember).subscribe({
      next: (d) => {
        this.errmessage = undefined;
        let id_studente = this.user_http.getId();

        if (this.pres_code != undefined && id_studente != undefined) {
          this.addAttendance(id_studente)
        } else {
          this.router.navigate(['/home']);
        }
      },
      error: (err) => {
        console.log('Login error: ' + JSON.stringify(err));
        this.errmessage = err.error.errormessage;
      }
    });
  }
}
