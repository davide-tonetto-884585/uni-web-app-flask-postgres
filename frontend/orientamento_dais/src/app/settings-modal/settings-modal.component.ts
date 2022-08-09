import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { SettingsHttpService } from '../settings-http.service';

@Component({
  selector: 'app-settings-modal',
  templateUrl: './settings-modal.component.html',
  styleUrls: ['./settings-modal.component.css']
})
export class SettingsModalComponent implements OnInit {
  settings: any;

  constructor(
    private settings_http: SettingsHttpService,
    private dialog: MatDialog
  ) { }

  ngOnInit(): void {
    this.settings_http.getCurrentSettings().subscribe({
      next: (res) => {
        this.settings = res.settings;
      }
    })
  }

  updateSettings(): void {
    this.settings_http.updateSettings(this.settings).subscribe({
      next: (res) => {
        this.dialog.closeAll();
      },
      error: (err) => {
        console.log(err)
      }
    })
  }
}
