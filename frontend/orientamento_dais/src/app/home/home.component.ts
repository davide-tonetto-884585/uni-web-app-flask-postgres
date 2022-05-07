import { Component, OnInit } from '@angular/core';

import { CourseHttpService } from '../course-http.service';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css'],
  providers: [
    {provide: CourseHttpService, useClass: CourseHttpService }
  ]
})
export class HomeComponent implements OnInit {

  constructor(
    private course_http: CourseHttpService
  ) { }

  ngOnInit(): void {
  }

}
