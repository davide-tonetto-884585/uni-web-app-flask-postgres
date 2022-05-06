import { Component, OnInit } from '@angular/core';

import { UserHttpService } from '../user-http.service';

@Component({
  selector: 'app-top-bar',
  templateUrl: './top-bar.component.html',
  styleUrls: ['./top-bar.component.css']
})
export class TopBarComponent implements OnInit {

  constructor(
    private user_http: UserHttpService
  ) { }

  ngOnInit(): void {
  }

  isLogged(): boolean {
    return this.user_http.isLogged();
  }

  getName(): string | boolean {
    return this.user_http.getName();
  }

}
