import { Component, OnInit } from '@angular/core';

import { UserHttpService } from '../user-http.service';
import { Router, ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-activate-profile',
  templateUrl: './activate-profile.component.html',
  styleUrls: ['./activate-profile.component.css']
})
export class ActivateProfileComponent implements OnInit {
  private activation_token: any;
  private user_id: any;
  category: any;
  user_data: any;
  errormessage: string | undefined;

  constructor(private user_http: UserHttpService, private router: Router, private activatedRoute: ActivatedRoute) { }

  ngOnInit(): void {
    this.activatedRoute.paramMap.subscribe(params => {
      this.activation_token = params.get('token');
      this.user_id = params.get('user_id');
      this.category = params.get('category');
    });
  }

  complete_registration(): void {
    this.user_http.complete_registration(this.user_id, this.activation_token, this.user_data).subscribe({
      next: (d) => {
        this.router.navigate(['/login']);
      },
      error: (err) => {
        console.log('Activation error: ' + JSON.stringify(err));
        this.errormessage = err.error.errormessage;
      }
    })
  }
}
