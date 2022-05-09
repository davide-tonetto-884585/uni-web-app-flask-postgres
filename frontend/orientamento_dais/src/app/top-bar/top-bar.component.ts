import { Component, OnInit } from '@angular/core';

import { UserHttpService } from '../user-http.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-top-bar',
  templateUrl: './top-bar.component.html',
  styleUrls: ['./top-bar.component.css']
})
export class TopBarComponent implements OnInit {

  constructor(
    private user_http: UserHttpService,
    private router: Router
  ) { }

  ngOnInit(): void {
  }

  getUrl(): string {
    return this.router.url;
  }

  isLogged(): boolean {
    return this.user_http.isLogged();
  }

  getName(): string | boolean {
    return this.user_http.getName();
  }

  logout(): void {
    this.user_http.logout();
  }

  isStudent(): boolean {
    return this.user_http.isStudent();
  }

  isTeacher(): boolean {
    return this.user_http.isTeacher();
  }
}
