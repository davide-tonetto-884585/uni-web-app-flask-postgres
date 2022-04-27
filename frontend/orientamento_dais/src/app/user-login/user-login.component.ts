import { Component, OnInit } from '@angular/core';
import { UserHttpService } from '../user-http.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-user-login',
  templateUrl: './user-login.component.html',
  styleUrls: ['./user-login.component.css']
})
export class UserLoginComponent implements OnInit {
  errmessage: string | undefined;

  constructor(private user_http: UserHttpService, private router: Router) { }

  ngOnInit(): void {
  }

  login(mail: string, password: string, remember: boolean) {
    this.user_http.login(mail, password, remember).subscribe({
      next: (d) => {
        this.errmessage = undefined;
        this.router.navigate(['/home']);
      },
      error: (err) => {
        console.log('Login error: ' + JSON.stringify(err));
        this.errmessage = err.error.errormessage;
      }
    });
  }
}
