from tastypie import paginator


class NoCountPaginator(paginator.Paginator):
    """Paginator class that avoids a COUNT query and provides no total count."""
    def get_count(self):
        return 0


    def page(self):
        output = super(NoCountPaginator, self).page()
        del output['meta']['total_count']
        return output


class PostPaginator(paginator.Paginator):
    """Adds a meta.more boolean attribute."""
    def page(self):
        output = super(PostPaginator, self).page()
        meta = output['meta']
        meta['more'] = meta['total_count'] > meta['limit']
        return output
