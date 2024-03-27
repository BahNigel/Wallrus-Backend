from django.urls import path

from . import views
from analytic_app.views import *
from follow_app.views import FollowArtistView
from invite.views import InviteView
from orders.views import *
from notifications.views import *
from cms.views import *

urlpatterns = [
     path('signup/', views.CustomUserCreate.as_view(), name='signup'),
     path('signup/<str:referral_code>', views.CustomUserCreate.as_view(), name='referral-signup'),
     path('verify-email-phone/', views.EmailPhoneView.as_view(), name='EmailPhoneView'),
     path('app-list/', views.AppList.as_view(), name='App_list'),
     path('verify-otp/', views.VerifyUserView.as_view(), name='VerifyUser'),
     path('validate-otp/', views.ValidateOtpView.as_view(), name='Validate-otp'),
     path('send-otp/', views.SendOTPView.as_view(), name='SendOTPView'),
     path('edit-detail/', views.Edit_Detail.as_view(), name='Edit_Detail'),
     path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
     path('notification-settings', views.NotificationSettings.as_view(), name='notification-settings'),
     path('subscribe-newsletter/', views.SubscribeNewsLetter.as_view(), name = 'subscribe-newsletter'),
     path('global-search/', views.GlobalSearchView.as_view(), name='global-search'),
     path('user-notification/', UserNotificationsView.as_view(), name='user-notification'),
     path('notification-mark-all-read/', MarkAllAsReadView.as_view(), name='notification-mark-all-read'),
     path('content/<str:section>', ContentView.as_view(), name='content'),
     path('social-user-details', views.SocilaUserDetailsView.as_view(), name='social-user-details'),
     path('social-user-detail/', views.Social_Edit_Detail.as_view(), name='social-user-detail'),

     # Artist Apis
     path('artist-snippet', views.ArtistSnippet.as_view(), name='artist-snippet'),
     path('artist-design-list/<id>', views.ArtistDesign.as_view(), name='artist-design-list'),
     path('design-tag-list', views.DesignTagList.as_view(), name='design-tag-list'),
     path('upload-design', views.UploadDesign.as_view(), name='upload-design'),
     path('under-review/', views.UnderReviewView.as_view(), name='under-review'),
     path('user-type/', views.UserTypeView.as_view(), name='user-type'),
     path('artist-details/<id>', views.ArtistDetails.as_view(), name='artist-details'),
     path('delete-design', views.DeleteDesign.as_view(), name='delete-design'),

     # Shop Apis
     path('material-list/<str:application_slug>', views.MaterialListView.as_view(), name='material-list'),
     path('filter-list/<str:application_slug>', views.FilterList.as_view(), name='tag-list'),
     path('product-list/<str:application_slug>', views.ApplicationProductList.as_view(), name='product-list'),
     path('product-detail/<str:product_slug>', views.ProductDetail.as_view(), name='product-detail'),
     path('featured-artist-list/', views.FeaturedArtistListView.as_view(), name='featured-artist-list'),
     path('other-colorways/<str:product_slug>', views.OtherColorways.as_view(), name='other-colorways'),
     path('other-applications/<str:product_slug>', views.OtherApplications.as_view(), name='other-applications'),
     path('similar-designs/<str:product_slug>', views.OtherColorways.as_view(), name='other-designs'),
     path('designer-list/<str:application_slug>/', views.DesignerListView.as_view(), name='designer-list'),
     path('filter-tag/', views.FilterTagList.as_view(), name='filter-tag'),
     path('latest-design/', views.LatestDesignList.as_view(), name='latest-design'),
     path('artist-list-status/', views.ArtistListStatus.as_view(), name='artist-list-status'),
     path('Design-list/', views.DesignListView.as_view(), name='Design-list'),
     path('product-review/', views.ProductReviewView.as_view(), name='product-review'),
     path('share-cart/', ShareCart.as_view(), name='share-cart'),
     path('client-list/', ClientDetailsView.as_view(), name='client-list'),
     path('purchase-request/', AddPurchaseRequest.as_view(), name='purchase-request'),

     # Clinet View
     path('client-view/', ClientCartView.as_view(), name='client-view'),
     path('client-initiate-order', InitiateClientOrder.as_view(), name='client-initiate-order'),
     path('client-place-order', ClientPlaceOrderView.as_view(), name='client-place-order'),
     path('client-address', ClientAddressView.as_view(), name='client-address'),
     

     # firm admin apis
     path('firm-user-snippet', views.FirmUserSnippet.as_view(), name='firm-user-snippet'),
     path('firm-user-list', views.FirmUsersList.as_view(), name='firm-user-list'),
     path('firm-order-list', views.FirmOrders.as_view(), name='firm-order-list'),
     path('sales-graph', views.SalesGraph.as_view(), name='sales-graph'),
     path('decorator-detail/<decorator_id>', views.IntDecoratorDetail.as_view(), name='decorator-detail'),
     path('card-detail', views.CardDetail.as_view(), name='card-detail'),
     path('purchase-requests-list', views.PurchaseRequestListView.as_view(), name='purchase-requests-list'),
     path('reject-purchase-request/<int:pk>', views.RejectPurchaseRequest.as_view(), name='reject-purchase-request'),
     path('accept-purchase-request/<int:pk>', views.AcceptPurchaseRequest.as_view(), name='accept-purchase-request'),
     path('add-user/', views.AddUser.as_view(), name='add-user'),
     path('search-decorator/', views.SearchDecoratorView.as_view(), name='search-decorator'),
     path('firm-initiate-order/', InitiateFirmOrder.as_view(), name='firm-initiate-order'),
     path('firm-place-order/', FirmPlaceOrderView.as_view(), name='firm-place-order'),
     path('firm-remove-user/', views.RemoveUserView.as_view(), name='firm-remove-user'),

     # wallrus-admin
     # Design list, detial, patch methods for wallrus-admin
     path('admin-design-list', views.DesignList.as_view(), name='admin-design-list'),
     path('admin-colorway-list', views.ColorwayList.as_view(), name='admin-design-list'),
     path('admin-design-detail/<int:design_id>', views.DesignDetail.as_view(), name='admin-design-detail'),
     path('design-status/<int:design_id>', views.ApproveDesign.as_view(), name='design-status'),
     
     # Blog post list, detail, create for wallrus-admin
     path('post-list', views.PostList.as_view(), name='post-list'),
     path('post-detail/<slug:post_slug>', views.PostDetail.as_view(), name='post-detail'),
     path('create-post', views.CreatePost.as_view(), name='create-post'),

     # Artist list, detail, status for wallrus-admin
     path('new-artists-list', views.NewArtists.as_view(), name='new-artists-list'),
     path('admin-artist-detail/<int:artist_id>', views.AdminArtistDetail.as_view(), name='admin-artist-detail'),
     path('artist-status/<int:artist_id>', views.ApproveArtist.as_view(), name='artist-status'),

     # Order list, detail, status for wallrus-admin
     path('order-list', views.OrderList.as_view(), name='order-list'),
     path('order-details/<int:order_id>', views.OrderDetail.as_view(), name='order-details'),
     path('order-status/<int:order_id>', views.ApproveOrder.as_view(), name='order-status'),
     # for wallrus-admin
     path('monthly-sales', views.MonthlySales.as_view(), name='monthly-sales'),
     path('decorators-count', views.MonthlyDecoratorsCount.as_view(), name='decorators-count'),
     path('artists-count', views.MonthlyArtistsCount.as_view(), name='artists-count'),
     path('bar-chart', views.MonthlyBarChart.as_view(), name='artists-count'),
     path('pie-chart', views.PieChart.as_view(), name='pie-chart'),

     # decorator apis
     path('decorator-snippet', views.DecoratorSnippet.as_view(), name='decorator-snippet'),
     path('add-to-favourites/<int:sku>',views.AddToFavourites.as_view(), name = 'add-to-favourites'),
     path('remove-from-favourites/<int:sku>',views.RemoveFromFavourites.as_view(), name = 'remove-from-favourites'),
     path('decorator-favourites', views.DecoratorFavourites.as_view(), name='decorator-favourites'),
     path('decorator-collections', views.DecoratorCollections.as_view(), name='decorator-collections'),
     path('decorator-collections/<int:pk>', views.DecoratorCollections.as_view(), name='decorator-collections-details'),
     path('my-order', views.MyOrder.as_view(), name='my-order'),
     path('cancel-order', CancelOrderView.as_view(), name='cancel-order'),
     path('customize-design', views.CustomizeDesign.as_view(), name='customize-design'),
     path('request-measurement', views.RequestMeasurement.as_view(), name='request-measurement'),
     path('upload-own-design', views.UploadOwnDesign.as_view(), name='upload-own-design'),
     path('password-reset/<uidb64>/<token>/', views.PasswordTokenCheckAPI.as_view(), name='password-reset'),
     path('reset-email', views.RequestPasswordResetEmail.as_view(), name='reset-email'),
     path('password-reset-complete', views.SetNewPassswordAPIView.as_view(), name='password-reset-complete'),
     path('add-address', views.AddAddress.as_view(), name='add-address'),
     path('initiate-order', InitiateOrder.as_view(), name='initiate-order'),
     path('place-order', PlaceOrderAPIView.as_view(), name='place-order'),
     path('get-post/<category>', views.GetPostList.as_view(), name='get-post'),
     path('get-fllowed-artist-product', views.FollowedArtistProduct.as_view(), name='get-fllowed-artist-product'),
     path('create-discount-coupon', CreateDiscoutCoupon.as_view(), name='create-discount-coupon'),
     path('coupon-details', CouponDetails.as_view(), name='coupon-details'),
     path('coin-transaction', views.CoinTransactionView.as_view(), name='coin-transaction'),
     path('decorator-levels', views.LevelListView.as_view(), name='decorator-levels'),
     

     path('business-analytic', BusinessAnalytic.as_view(), name='business-analytic'),
     path('platinum-business-analytic', PlatinumArtistBusinessAnalytic.as_view(), name='platinum-business-analytic'),
     path('follow-artist', FollowArtistView.as_view(), name='follow-artist'),
     path('invite-friend', InviteView.as_view(), name='invite-friend'),
     path('add-to-cart', CartView.as_view(), name='add-to-cart'),
     path('add-to-cart/<int:pk>', CartView.as_view(), name='add-to-cart'),
     # For Wallrus Admin
     path('new-decorator-list', views.NewDecoratorsView.as_view(), name='new-decorator-list'),
     path('new-decorator-list/<int:decorator_id>', views.NewDecoratorsView.as_view(), name='new-decorator-patch'),
     path('request-measurement-list', views.RequestMeasurementVerifyView.as_view(), name='request-measurement-list'),
     path('request-measurement-list/<int:request_measurement_id>', views.RequestMeasurementVerifyView.as_view(), name='request-measurement-patch'),
     path('design-tag', views.DesignTagVerifyView.as_view(), name='design-tag'),
     path('design-tag/<int:design_tag_id>', views.DesignTagVerifyView.as_view(), name='design-tag'),
]