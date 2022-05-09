import { Component, OnInit, Input, HostBinding } from '@angular/core';

@Component({
  selector: 'app-carousel-item',
  templateUrl: './carousel-item.component.html',
  host: { class: 'carousel-item' },
  styleUrls: ['./carousel-item.component.css']
})
export class CarouselItemComponent implements OnInit {
  @Input() active: boolean = false;
  @HostBinding('class.active') classActive: boolean = false;

  constructor() { }

  ngOnInit(): void {
    if (this.active) {
      this.classActive = true;
    }
  }

}
